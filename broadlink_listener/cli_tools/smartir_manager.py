# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""SmartIR json manager class."""

import json
import time
from enum import Enum
from itertools import product
from pathlib import Path

import click

from broadlink_listener.cli_tools.broadlink_manager import BroadlinkManager


class _DictKeys(Enum, str):
    CONTROLLER = "supportedController"
    TEMPERATURE = "temperature"
    MIN_TEMP = "minTemperature"
    MAX_TEMP = "maxTemperature"
    PRECISION = "precision"
    OPERATION_MODES = "operationModes"
    FAN_MODES = "fanModes"
    SWING_MODES = "swingModes"
    COMMANDS = "commands"


def _countdown(msg: str):
    click.echo(msg)
    for i in range(5, 0, -1):
        click.echo(i)
        time.sleep(1)


class SmartIrManager:
    """Manager class for SmartIR json."""

    def __init__(self, file_name: Path, broadlink_mng: BroadlinkManager):
        """SmartIR Manager.

        Arguments:
            file_name: SmartIR json file that contains basic structure of codes to be recorded.
            broadlink_mng: Broadlink Manager object used to listen IR codes

        Raises:
            UsageError: raised if controller is not Broadlink or no IR signal is learnt during the process
        """
        self.__broadlink_manager = broadlink_mng

        self.__json_file_name = file_name
        with open(str(file_name), "r", encoding='utf-8') as in_file:
            self.__smartir_dict = json.load(in_file)

        self.__all_combinations = tuple()
        try:
            _controller = self.__smartir_dict[_DictKeys.CONTROLLER]
            if _controller != "Broadlink":
                raise click.exceptions.UsageError(f"Controller {_controller} not supported")

            self.__min_temp = int(self.__smartir_dict[_DictKeys.MIN_TEMP])
            self.__max_temp = int(self.__smartir_dict[_DictKeys.MAX_TEMP])
            self.__precision_temp = int(self.__smartir_dict.get(_DictKeys.PRECISION, 1))
            self.__op_modes = self.__smartir_dict[_DictKeys.OPERATION_MODES]
            self.__fan_modes = self.__smartir_dict.get(_DictKeys.FAN_MODES, None)
            self.__swing_modes = self.__smartir_dict.get(_DictKeys.SWING_MODES, None)

        except KeyError as key_err:
            raise click.exceptions.UsageError(f"Missing mandatory field in json file: {key_err}") from None
        else:
            self._setup_combinations()
            self.__temperature = ''
            self.__operation_mode = ''
            self.__fan_mode = ''
            self.__swing_mode = ''
            self.__combination_arguments = tuple()

    def _setup_combinations(self):
        _variable_args = [self.__fan_modes, self.__swing_modes]
        if all(_variable_args):
            self.__all_combinations = product(
                self.__op_modes,
                self.__fan_modes,
                self.__swing_modes,
                range(self.__min_temp, self.__max_temp + 1, self.__precision_temp),
            )
            self.__combination_arguments = (
                _DictKeys.OPERATION_MODES,
                _DictKeys.FAN_MODES,
                _DictKeys.SWING_MODES,
                _DictKeys.TEMPERATURE,
            )
        else:
            if any(_variable_args):
                if self.__swing_modes:
                    self.__all_combinations = product(
                        self.__op_modes,
                        self.__swing_modes,
                        range(self.__min_temp, self.__max_temp + 1, self.__precision_temp),
                    )
                    self.__combination_arguments = (
                        _DictKeys.OPERATION_MODES,
                        _DictKeys.SWING_MODES,
                        _DictKeys.TEMPERATURE,
                    )
                else:
                    self.__all_combinations = product(
                        self.__op_modes,
                        self.__fan_modes,
                        range(self.__min_temp, self.__max_temp + 1, self.__precision_temp),
                    )
                    self.__combination_arguments = (
                        _DictKeys.OPERATION_MODES,
                        _DictKeys.FAN_MODES,
                        _DictKeys.TEMPERATURE,
                    )
            else:
                self.__all_combinations = product(
                    self.__op_modes, range(self.__min_temp, self.__max_temp + 1, self.__precision_temp)
                )
                self.__combination_arguments = (_DictKeys.OPERATION_MODES, _DictKeys.TEMPERATURE)

    @property
    def temperature(self) -> str:
        """Temperature key saved to json."""
        return self.__temperature

    @temperature.setter
    def temperature(self, new_value: str) -> None:
        """Set Temperature key."""
        self.__temperature = new_value

    @property
    def operation_mode(self) -> str:
        """Operation Mode key saved to json."""
        return self.__operation_mode

    @operation_mode.setter
    def operation_mode(self, new_value: str) -> None:
        """Set Operation Mode key."""
        self.__operation_mode = new_value

    @property
    def fan_mode(self) -> str:
        """Fan Mode key saved to json."""
        return self.__fan_mode

    @fan_mode.setter
    def fan_mode(self, new_value: str) -> None:
        """Set Fan Mode key."""
        self.__fan_mode = new_value

    @property
    def swing_mode(self) -> str:
        """Swing Mode key saved to json."""
        return self.__swing_mode

    @swing_mode.setter
    def swing_mode(self, new_value: str) -> None:
        """Set Swing Mode key."""
        self.__swing_mode = new_value

    def set_dict_value(self, value: str) -> None:
        """Set value to output dict having previously set keys."""
        if _DictKeys.FAN_MODES in self.__combination_arguments:
            if _DictKeys.SWING_MODES in self.__combination_arguments:
                self.__smartir_dict[_DictKeys.COMMANDS][self.operation_mode][self.fan_mode][self.swing_mode][self.temperature] = value
            else:
                self.__smartir_dict[_DictKeys.COMMANDS][self.operation_mode][self.fan_mode][self.temperature] = value
        else:
            if _DictKeys.SWING_MODES in self.__combination_arguments:
                self.__smartir_dict[_DictKeys.COMMANDS][self.operation_mode][self.swing_mode][self.temperature] = value
            else:
                self.__smartir_dict[_DictKeys.COMMANDS][self.operation_mode][self.temperature] = value

    def save_dict(self):
        """Save modified dict to output json file."""
        _modified_file_name = Path(self.__json_file_name.parent).joinpath(f"{self.__json_file_name.stem}.json")
        with open(_modified_file_name, 'w', encoding='utf-8') as out_file:
            json.dump(self.__smartir_dict, out_file)

    def learn_off(self):
        """Learn OFF command that's outside the combination."""
        _countdown("First of all, let's learn OFF command: turn ON the remote and then turn it OFF when "
                   "'Listening' message is on screen...")
        _off = self.__broadlink_manager.learn_single_code()
        if not _off:
            raise click.exceptions.UsageError("No IR signal learnt for OFF command.")
        self.__smartir_dict[_DictKeys.COMMANDS]["off"] = _off

    def lear_all(self):
        """Learn all the commands depending on calculated combination."""
        for comb in self.__all_combinations:
            _str = '- '.join(comb)
            _countdown(f"Let's learn {_str} command: turn ON the remote and then turn it OFF when "
                       "'Listening' message is on screen...")

