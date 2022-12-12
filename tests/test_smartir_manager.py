# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Test smartir manager module."""

from unittest.mock import Mock

import click
import pytest

from broadlink_listener.cli_tools.smartir_manager import SmartIrManager


class TestSmartIR:
    """SmartIR manager test class."""

    def test_not_broadlink(self, json_file_not_broadlink):
        """Test controller not supported.

        Arguments:
            json_file_not_broadlink: pytest fixture
        """
        with pytest.raises(click.exceptions.UsageError):
            _ = SmartIrManager(json_file_not_broadlink, Mock())

    def test_not_base64(self, json_file_not_base64):
        """Test encoding not supported.

        Arguments:
            json_file_not_base64: pytest fixture
        """
        with pytest.raises(click.exceptions.UsageError):
            _ = SmartIrManager(json_file_not_base64, Mock())

    def test_missing_min_temp(self, json_file_missing_min_temp):
        """Test missing min temp.

        Arguments:
            json_file_missing_min_temp: pytest fixture
        """
        with pytest.raises(click.exceptions.UsageError):
            _ = SmartIrManager(json_file_missing_min_temp, Mock())

    def test_missing_max_temp(self, json_file_missing_max_temp):
        """Test missing max temp.

        Arguments:
            json_file_missing_max_temp: pytest fixture
        """
        with pytest.raises(click.exceptions.UsageError):
            _ = SmartIrManager(json_file_missing_max_temp, Mock())

    def test_missing_operation_modes(self, json_file_missing_operation_modes):
        """Test missing operation mode.

        Arguments:
            json_file_missing_operation_modes: pytest fixture
        """
        with pytest.raises(click.exceptions.UsageError):
            _ = SmartIrManager(json_file_missing_operation_modes, Mock())
