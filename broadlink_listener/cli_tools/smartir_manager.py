# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""SmartIR json manager class."""

import json
import time
from collections import namedtuple
from datetime import datetime
from enum import Enum
from itertools import product
from pathlib import Path
from typing import Union

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


def _countdown(msg: str):
    click.echo(msg)
    for i in range(5, 0, -1):
        click.echo(i)
        time.sleep(1)


class SmartIrManager:  # pylint: disable=too-many-instance-attributes
    """Manager class for SmartIR json."""

    def __init__(
        self, file_name: Path, broadlink_mng: BroadlinkManager, no_temp_on_mode: tuple, no_swing_on_mode: tuple
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

        self.__json_file_name = file_name
        with open(str(file_name), "r", encoding='utf-8') as in_file:
            self.__smartir_dict = json.load(in_file)

        self.__all_combinations: tuple = ()
        self.__no_temp_on_modes: tuple = no_temp_on_mode
        self.__no_swing_on_modes: tuple = no_swing_on_mode
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

        except KeyError as key_err:
            raise click.exceptions.UsageError(f"Missing mandatory field in json file: {key_err}") from None
        else:
            self._setup_combinations()
            self.__temperature = ''
            self.__operation_mode = ''
            self.__fan_mode = ''
            self.__swing_mode = ''
            self.__combination_arguments: tuple = ()

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
                    self.__combination_arguments = _combination_arguments_all
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

    def save_dict(self):
        """Save modified dict to output json file."""
        now = datetime.now()
        _modified_file_name = Path(self.__json_file_name.parent).joinpath(
            f'{self.__json_file_name.stem}_' f'{now.strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(_modified_file_name, 'w', encoding='utf-8') as out_file:
            json.dump(self.__smartir_dict, out_file)

    def learn_off(self):
        """Learn OFF command that's outside the combination.

        Raises:
            UsageError: if no IR signal is learnt within timeout
        """
        _countdown(
            "First of all, let's learn OFF command: turn ON the remote and then turn it OFF when "
            "'Listening' message is on screen..."
        )
        _off = self.__broadlink_manager.learn_single_code()
        if not _off:
            raise click.exceptions.UsageError("No IR signal learnt for OFF command within timeout.")
        self.__smartir_dict[_DictKeys.COMMANDS.value]["off"] = _off

    def lear_all(self):
        """Learn all the commands depending on calculated combination.

        Raises:
            UsageError: if no IR signal is learnt within timeout
        """
        _first_code_learnt_when_skip = False
        _previous_code = None
        for comb in self.__all_combinations:
            self.operation_mode = comb.operationModes
            if _DictKeys.FAN_MODES in comb:
                self.fan_mode = comb.fanModes
            if _DictKeys.SWING_MODES in comb:
                self.swing_mode = comb.swingModes
            self.temperature = comb.temperature

            if self._skip_learning(comb):
                if _first_code_learnt_when_skip:
                    self._set_dict_value(_previous_code)
                    continue

                _first_code_learnt_when_skip = True

            _combination_str = self._get_combination(comb)
            _countdown(
                f"Let's learn command of\n{_combination_str}\n"
                "Prepare the remote to this combination, then turn it OFF. When 'Listening' message"
                " is on screen, turn the remote ON to learn combination previously set..."
            )
            _code = self.__broadlink_manager.learn_single_code()
            _previous_code = _code
            if not _code:
                raise click.exceptions.UsageError(f"No IR signal learnt for {_combination_str} command within timeout.")

            self._set_dict_value(_code)

    def _get_combination(self, combination: tuple) -> str:
        _mixed = zip(self.__combination_arguments, combination)
        _ret = []
        for _m in _mixed:
            _ret.append(' = '.join(_m))
        return '\n'.join(_ret)

    def _skip_learning(
        self, comb: Union[_CombinationTupleAll, _CombinationTupleSwing, _CombinationTupleFan, _CombinationTupleNone]
    ) -> bool:
        _ret = False
        if _DictKeys.SWING_MODES in comb._fields and comb.operationModes in self.__no_swing_on_modes:  # type: ignore
            _ret = True
        if comb.operationModes in self.__no_temp_on_modes:  # type: ignore
            _ret = True
        return _ret
