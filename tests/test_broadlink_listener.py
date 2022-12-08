#!/usr/bin/env python

# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Tests for `broadlink_listener` package."""

import pytest
from click.testing import CliRunner

from broadlink_listener.cli_tools import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.

    Arguments:
        response: pytest feature
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    del response


def test_command_line_interface_help():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '  --help     Show this message and exit.' in help_result.output


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
