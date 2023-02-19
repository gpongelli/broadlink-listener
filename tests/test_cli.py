# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Tests for `broadlink_listener` package."""

from unittest.mock import Mock, patch

from broadlink_listener import __version__
from broadlink_listener.cli_tools import cli


def test_command_line_interface_help(runner):
    """Test the CLI.

    Arguments:
        runner: pytest click CliRunner object
    """
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '  --help     Show this message and exit.' in help_result.output


def test_command_line_interface_version(runner):
    """Test the CLI.

    Arguments:
        runner: pytest click CliRunner object
    """
    help_result = runner.invoke(cli.main, ['--version'])
    assert help_result.exit_code == 0
    assert __version__ in help_result.output


def test_generation_smart_ir(runner, json_file_good_data_op_swing_mode):
    """Test the CLI.

    Arguments:
        runner: pytest click CliRunner object
        json_file_good_data_op_swing_mode: existing json file
    """
    with patch('broadlink.remote.rmmini.enter_learning'), patch(
        'broadlink.device.Device.auth', Mock(return_value=True)
    ), patch('broadlink_listener.cli_tools.broadlink_manager.BroadlinkManager'), patch(
        'broadlink_listener.cli_tools.smartir_manager.SmartIrManager.learn_off'
    ) as _learn_off, patch(
        'broadlink_listener.cli_tools.smartir_manager.SmartIrManager.learn_all'
    ) as _learn_all, patch(
        'broadlink_listener.cli_tools.smartir_manager.SmartIrManager.save_dict'
    ) as _save:
        _ = runner.invoke(
            cli.main, ['generate-smart-ir', str(json_file_good_data_op_swing_mode), '0x1234', '192.168.1.1', '12345678']
        )
        _learn_off.assert_called_once()
        _learn_all.assert_called_once()
        _save.assert_called_once()


def test_py_version():
    """Dummy test to print python version used by pytest."""
    import sys

    print(f"in TEST: {sys.version}  -- {sys.version_info}")
    # if sys.version_info <= (3, 9, 18):
    #     # 3.9 OK
    #     assert True
    # else:
    #     # 3.10 FAIL
    #     assert False
