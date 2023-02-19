# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""SmartIR json manager class."""

import glob
import json
import os
import platform
import re
import signal
import sys
from collections import namedtuple
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from itertools import product
from pathlib import Path
from threading import Event
from typing import Literal, Optional, Union

import click

from broadlink_listener.cli_tools.broadlink_manager import BroadlinkManager


class _DictKeys(str, Enum):
    CONTROLLER = "supportedController"
    TEMPERATURE = "temperature"
    MIN_TEMP = "minTemperature"
    MAX_TEMP = "maxTemperature"
    PRECISION = "precision"
    OPERATION_MODES = "operationModes"
    FAN_MODES = "fanModes"
    SWING_MODES = "swingModes"
    COMMANDS = "commands"
    COMMANDS_ENCODING = "commandsEncoding"


@dataclass
class SkipReason:
    """Data class to describe skip reason."""

    skip: bool
    field: Optional[Union[Literal[_DictKeys.SWING_MODES], Literal[_DictKeys.TEMPERATURE]]]


_combination_arguments_all = (
    _DictKeys.OPERATION_MODES.value,
    _DictKeys.FAN_MODES.value,
    _DictKeys.SWING_MODES.value,
    _DictKeys.TEMPERATURE.value,
)

_combination_arguments_swing = (
    _DictKeys.OPERATION_MODES.value,
    _DictKeys.SWING_MODES.value,
    _DictKeys.TEMPERATURE.value,
)

_combination_arguments_fan = (
    _DictKeys.OPERATION_MODES.value,
    _DictKeys.FAN_MODES.value,
    _DictKeys.TEMPERATURE.value,
)

_combination_arguments_none = (
    _DictKeys.OPERATION_MODES.value,
    _DictKeys.TEMPERATURE.value,
)


_CombinationTupleAll = namedtuple('_CombinationTupleAll', ', '.join(_combination_arguments_all))  # type: ignore

_CombinationTupleSwing = namedtuple('_CombinationTupleSwing', ', '.join(_combination_arguments_swing))  # type: ignore

_CombinationTupleFan = namedtuple('_CombinationTupleFan', ', '.join(_combination_arguments_fan))  # type: ignore

_CombinationTupleNone = namedtuple('_CombinationTupleNone', ', '.join(_combination_arguments_none))  # type: ignore


def _countdown(msg: str, event: Event):
    click.echo(msg)
    if event.is_set():
        input("-->> Press enter when ready <<--")
    event.clear()


class SmartIrManager:  # pylint: disable=too-many-instance-attributes
    """Manager class for SmartIR json."""

    def __init__(  # pylint: disable=too-many-branches,too-many-statements
        self,
        file_name: Path,
        broadlink_mng: BroadlinkManager,
        no_temp_on_mode: tuple = tuple(),
        no_swing_on_mode: tuple = tuple(),
    ):
        """Smart IR Manager.

        Arguments:
            file_name: SmartIR json file that contains basic structure of codes to be recorded.
            broadlink_mng: Broadlink Manager object used to listen IR codes
            no_temp_on_mode: option, that can be set multiple times, related to operating mode that have no temperature
                         selection
            no_swing_on_mode: option, that can be set multiple times, related to operating mode that have no swing
                          selection

        Raises:
            UsageError: raised if controller is not Broadlink or no IR signal is learnt during the process
        """
        self.__broadlink_manager = broadlink_mng

        self.__partial_inc = 0
        self.__prompt_event = Event()
        self.__prompt_event.clear()
        self.__json_file_name_path = Path(file_name)
        with open(str(file_name), "r", encoding='utf-8') as in_file:
            self.__smartir_dict = json.load(in_file)

        self.__all_combinations: tuple = ()
        self.__no_temp_on_modes: tuple = no_temp_on_mode
        self.__no_swing_on_modes: tuple = no_swing_on_mode
        self.__swing_saved_temp: dict = {}
        try:
            _controller = self.__smartir_dict[_DictKeys.CONTROLLER.value]
            if _controller != "Broadlink":
                raise click.exceptions.UsageError(f"Controller {_controller} not supported")

            _commands_encoding = self.__smartir_dict[_DictKeys.COMMANDS_ENCODING.value]
            if _commands_encoding != "Base64":
                raise click.exceptions.UsageError(f"Encoding {_commands_encoding} not supported")

            self.__min_temp = int(self.__smartir_dict[_DictKeys.MIN_TEMP.value])
            self.__max_temp = int(self.__smartir_dict[_DictKeys.MAX_TEMP.value])
            self.__precision_temp = int(self.__smartir_dict.get(_DictKeys.PRECISION.value, 1))
            self.__op_modes = self.__smartir_dict[_DictKeys.OPERATION_MODES.value]
            self.__fan_modes = self.__smartir_dict.get(_DictKeys.FAN_MODES.value, None)
            self.__swing_modes = self.__smartir_dict.get(_DictKeys.SWING_MODES.value, None)

            if not all(list(map(lambda x: x in self.__op_modes, no_swing_on_mode))):
                raise click.exceptions.UsageError("no-swing-on-mode parameter is using a not-existent operating mode.")

            if not all(list(map(lambda x: x in self.__op_modes, no_temp_on_mode))):
                raise click.exceptions.UsageError("no-temp-on-mode parameter is using a not-existent operating mode.")

            # fill dict with all empty combination
            _temp_dict = {
                f"{t}": deepcopy('') for t in range(self.__min_temp, self.__max_temp + 1, self.__precision_temp)
            }
            _swing_dict = None
            if self.__swing_modes:
                _swing_dict = {f"{s}": deepcopy(_temp_dict) for s in self.__swing_modes}
            else:
                if no_swing_on_mode:
                    raise click.exceptions.UsageError(
                        "Add swing to JSON file or do not use --no-swing-on-mode parameter."
                    )
            _fan_mode_dict = None
            if self.__fan_modes:
                if _swing_dict:
                    _fan_mode_dict = {f"{f}": deepcopy(_swing_dict) for f in self.__fan_modes}
                else:
                    _fan_mode_dict = {f"{f}": deepcopy(_temp_dict) for f in self.__fan_modes}  # type: ignore
                _operation_dict = {f"{o}": deepcopy(_fan_mode_dict) for o in self.__op_modes}
            else:
                if _swing_dict:
                    _operation_dict = {f"{o}": deepcopy(_swing_dict) for o in self.__op_modes}  # type: ignore
                else:
                    _operation_dict = {f"{o}": deepcopy(_temp_dict) for o in self.__op_modes}  # type: ignore
            self.__smartir_dict[_DictKeys.COMMANDS].update(_operation_dict)

            # overwrite combination if tmp file exist
            self._load_partial_dict()

        except KeyError as key_err:
            raise click.exceptions.UsageError(f"Missing mandatory field in json file: {key_err}") from None
        else:
            self._setup_combinations()
            self.__temperature = ''
            self.__operation_mode = ''
            self.__fan_mode = ''
            self.__swing_mode = ''
        self._setup_signal_handler()

    @property
    def smartir_dict(self) -> dict:
        """Output dictionary, for test purpose.

        Returns:
            dict: smartir compatible dictionary with learnt codes.
        """
        return self.__smartir_dict

    def _setup_signal_handler(self):
        _system = platform.system().lower()
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGABRT, self._signal_handler)

        if _system in ('linux', 'darwin'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if _system == 'windows':
            signal.signal(signal.SIGBREAK, self._signal_handler)  # pylint: disable=no-member
            signal.signal(signal.CTRL_C_EVENT, self._signal_handler)  # pylint: disable=no-member
            signal.signal(signal.CTRL_BREAK_EVENT, self._signal_handler)  # pylint: disable=no-member

    def _signal_handler(self, _signumber, _frame):
        self._save_partial_dict()
        sys.exit(2)

    def _setup_combinations(self):
        _variable_args = [self.__fan_modes, self.__swing_modes]
        if all(_variable_args):
            __combinations = product(
                self.__op_modes,
                self.__fan_modes,
                self.__swing_modes,
                range(self.__min_temp, self.__max_temp + 1, self.__precision_temp),
            )

            def _return_named_tuple():
                for _c in __combinations:
                    yield _CombinationTupleAll(_c[0], _c[1], _c[2], _c[3])

            self.__all_combinations = _return_named_tuple()
            self.__combination_arguments = _combination_arguments_all
        else:
            if any(_variable_args):
                if self.__swing_modes:
                    __combinations = product(
                        self.__op_modes,
                        self.__swing_modes,
                        range(self.__min_temp, self.__max_temp + 1, self.__precision_temp),
                    )

                    def _return_named_tuple():
                        for _c in __combinations:
                            yield _CombinationTupleSwing(_c[0], _c[1], _c[2])

                    self.__all_combinations = _return_named_tuple()
                    self.__combination_arguments = _combination_arguments_swing
                else:
                    __combinations = product(
                        self.__op_modes,
                        self.__fan_modes,
                        range(self.__min_temp, self.__max_temp + 1, self.__precision_temp),
                    )

                    def _return_named_tuple():
                        for _c in __combinations:
                            yield _CombinationTupleFan(_c[0], _c[1], _c[2])

                    self.__all_combinations = _return_named_tuple()
                    self.__combination_arguments = _combination_arguments_fan
            else:
                __combinations = product(
                    self.__op_modes, range(self.__min_temp, self.__max_temp + 1, self.__precision_temp)
                )

                def _return_named_tuple():
                    for _c in __combinations:
                        yield _CombinationTupleNone(_c[0], _c[1])

                self.__all_combinations = _return_named_tuple()
                self.__combination_arguments = _combination_arguments_none

    @property
    def temperature(self) -> str:
        """Temperature key saved to json.

        Returns:
            str: temperature string to be saved
        """
        return self.__temperature

    @temperature.setter
    def temperature(self, new_value: str) -> None:
        """Set Temperature key.

        Arguments:
            new_value: value to be set
        """
        self.__temperature = new_value

    @property
    def operation_mode(self) -> str:
        """Operation Mode key saved to json.

        Returns:
            str: operation mode string to be saved
        """
        return self.__operation_mode

    @operation_mode.setter
    def operation_mode(self, new_value: str) -> None:
        """Set Operation Mode key.

        Arguments:
            new_value: value to be set
        """
        self.__operation_mode = new_value

    @property
    def fan_mode(self) -> str:
        """Fan Mode key saved to json.

        Returns:
            str: fan mode string to be saved
        """
        return self.__fan_mode

    @fan_mode.setter
    def fan_mode(self, new_value: str) -> None:
        """Set Fan Mode key.

        Arguments:
            new_value: value to be set
        """
        self.__fan_mode = new_value

    @property
    def swing_mode(self) -> str:
        """Swing Mode key saved to json.

        Returns:
            str: swing mode string to be saved
        """
        return self.__swing_mode

    @swing_mode.setter
    def swing_mode(self, new_value: str) -> None:
        """Set Swing Mode key.

        Arguments:
            new_value: value to be set
        """
        self.__swing_mode = new_value

    @property
    def partial_inc(self) -> int:
        """Partial increment value.

        Returns:
            int: last index of saved partial json files
        """
        return self.__partial_inc

    def _set_dict_value(self, value: str) -> None:
        if _DictKeys.FAN_MODES in self.__combination_arguments:
            if _DictKeys.SWING_MODES in self.__combination_arguments:
                self.__smartir_dict[_DictKeys.COMMANDS.value][self.operation_mode][self.fan_mode][self.swing_mode][
                    self.temperature
                ] = value
            else:
                self.__smartir_dict[_DictKeys.COMMANDS.value][self.operation_mode][self.fan_mode][
                    self.temperature
                ] = value
        else:
            if _DictKeys.SWING_MODES in self.__combination_arguments:
                self.__smartir_dict[_DictKeys.COMMANDS.value][self.operation_mode][self.swing_mode][
                    self.temperature
                ] = value
            else:
                self.__smartir_dict[_DictKeys.COMMANDS.value][self.operation_mode][self.temperature] = value

    def _get_dict_value(self) -> str:
        _value = ''
        if _DictKeys.FAN_MODES in self.__combination_arguments:
            if _DictKeys.SWING_MODES in self.__combination_arguments:
                _value = self.__smartir_dict[_DictKeys.COMMANDS.value][self.operation_mode][self.fan_mode][
                    self.swing_mode
                ][self.temperature]
            else:
                _value = self.__smartir_dict[_DictKeys.COMMANDS.value][self.operation_mode][self.fan_mode][
                    self.temperature
                ]
        else:
            if _DictKeys.SWING_MODES in self.__combination_arguments:
                _value = self.__smartir_dict[_DictKeys.COMMANDS.value][self.operation_mode][self.swing_mode][
                    self.temperature
                ]
            else:
                _value = self.__smartir_dict[_DictKeys.COMMANDS.value][self.operation_mode][self.temperature]
        return _value

    def save_dict(self):
        """Save modified dict to output json file."""
        now = datetime.now()
        _modified_file_name = self.__json_file_name_path.parent.joinpath(
            f'{self.__json_file_name_path.stem}_{now.strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(_modified_file_name, 'w', encoding='utf-8') as out_file:
            json.dump(self.__smartir_dict, out_file)
        click.echo(f"Created new file {_modified_file_name}")
        _previous = glob.glob(
            os.path.join(self.__json_file_name_path.parent, f'{self.__json_file_name_path.stem}_tmp_*.json')
        )
        for _file in _previous:
            os.remove(_file)

    def _save_partial_dict(self):
        # save with incremental 3 numbers to sort correctly when load
        _modified_file_name = self.__json_file_name_path.parent.joinpath(
            f'{self.__json_file_name_path.stem}_tmp_{self.__partial_inc:03}.json'
        )

        try:
            _no_off = deepcopy(self.__smartir_dict)
            del _no_off['commands']['off']
        except KeyError:
            return
        else:
            with open(_modified_file_name, 'w', encoding='utf-8') as out_file:
                json.dump(_no_off[_DictKeys.COMMANDS.value], out_file, indent=2)
            self.__partial_inc += 1

    def _load_partial_dict(self):
        _previous = glob.glob(
            os.path.join(self.__json_file_name_path.parent, f'{self.__json_file_name_path.stem}_tmp_*.json')
        )
        _previous.sort()
        try:
            # load last file that's the most updated
            _last_file = _previous[-1]
            with open(str(_last_file), "r", encoding='utf-8') as partial_file:
                self.__smartir_dict[_DictKeys.COMMANDS.value].update(json.load(partial_file))
            _pattern = re.compile(fr'{self.__json_file_name_path.stem}_tmp_(\d+).json')
            _res = _pattern.search(_last_file)
            self.__partial_inc = int(_res.group(1))
        except IndexError:
            pass

    def learn_off(self):
        """Learn OFF command that's outside the combination.

        Raises:
            UsageError: if no IR signal is learnt within timeout
        """
        self.__prompt_event.clear()
        _countdown(
            "First of all, let's learn OFF command:\nturn ON the remote and then turn it OFF when "
            "'Listening' message is on screen, or interrupt with CTRL-C...",
            self.__prompt_event,
        )
        # set event to wait for first code
        self.__prompt_event.set()
        _off = self.__broadlink_manager.learn_single_code()
        if not _off:
            raise click.exceptions.UsageError("No IR signal learnt for OFF command within timeout.")
        self.__smartir_dict[_DictKeys.COMMANDS.value]["off"] = _off

    def learn_all(self):  # pylint: disable=too-many-branches
        """Learn all the commands depending on calculated combination.

        Raises:
            UsageError: if no IR signal is learnt within timeout
        """
        _previous_code = None
        _previous_combination: Optional[tuple] = None
        for comb in self.__all_combinations:  # pylint: disable=too-many-nested-blocks
            self.operation_mode = comb.operationModes
            if _DictKeys.FAN_MODES in comb._fields:
                self.fan_mode = comb.fanModes
            if _DictKeys.SWING_MODES in comb._fields:
                self.swing_mode = comb.swingModes
            self.temperature = str(comb.temperature)

            if self._get_dict_value() != '':
                self.__prompt_event.set()
                continue

            _do_skip = self._skip_learning(comb)
            if _do_skip.skip:
                # must read the first temperature and then reuse the same for next combination
                if _do_skip.field == _DictKeys.TEMPERATURE:
                    if comb.temperature > self.__min_temp:
                        # code @ min_temp already recorded
                        self._set_dict_value(_previous_code)
                        continue

                if _do_skip.field == _DictKeys.SWING_MODES:
                    _previous_code = self.__swing_saved_temp.get(self.temperature, None)
                    if _previous_code:
                        if isinstance(_previous_code, dict):
                            # there also is the fan level saved
                            _temp_code = _previous_code.get(self.fan_mode)
                            if _temp_code:
                                self._set_dict_value(_temp_code)
                                continue
                        else:
                            # no fan
                            self._set_dict_value(_previous_code)
                            continue

            if _previous_combination:
                for i in range(0, len(comb) - 1):
                    if _previous_combination[i] != comb[i]:  # pylint: disable=unsubscriptable-object
                        self.__prompt_event.set()
                        self._save_partial_dict()
            _previous_combination = comb

            _combination_str = self._get_combination(comb)
            _countdown(
                "-" * 30 + f"\nLet's learn IR command of\n{_combination_str}\n"
                "Prepare the remote so Broadlink can listen the above combination when 'Listening' message"
                " is on screen, or interrupt with CTRL-C...",
                self.__prompt_event,
            )
            _code = self.__broadlink_manager.learn_single_code()
            _previous_code = _code
            if not _code:
                self._save_partial_dict()
                raise click.exceptions.UsageError(f"No IR signal learnt for {_combination_str} command within timeout.")

            # swing modes must be saved because all temperature need to be listened
            if _do_skip.skip and _do_skip.field == _DictKeys.SWING_MODES:
                if _DictKeys.FAN_MODES in comb._fields:
                    self.__swing_saved_temp[self.temperature] = {self.fan_mode: _code}
                else:
                    self.__swing_saved_temp[self.temperature] = _code

            self._set_dict_value(_code)
        click.echo("All combination learnt.")

    def _get_combination(self, combination: tuple) -> str:
        _mixed = zip(self.__combination_arguments, combination)
        _ret = []
        for _m, _v in _mixed:
            _ret.append(f'-> {_m} = {_v}')
        return '\n'.join(_ret)

    def _skip_learning(
        self, comb: Union[_CombinationTupleAll, _CombinationTupleSwing, _CombinationTupleFan, _CombinationTupleNone]
    ) -> SkipReason:
        _ret = SkipReason(False, None)
        # swing mode is optional, so need its check
        if _DictKeys.SWING_MODES in comb._fields and comb.operationModes in self.__no_swing_on_modes:  # type: ignore
            _ret = SkipReason(True, _DictKeys.SWING_MODES)
        if comb.operationModes in self.__no_temp_on_modes:  # type: ignore
            _ret = SkipReason(True, _DictKeys.TEMPERATURE)
        return _ret
