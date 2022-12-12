# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Tests for `broadlink_listener` package."""

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
