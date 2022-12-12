# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Pytest conftest."""

from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture
def json_file_not_broadlink() -> Path:
    """Return json test file with not supported controller.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("data").joinpath("not_broadlink.json")


@pytest.fixture
def json_file_not_base64() -> Path:
    """Return json test file with not supported encoding.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("data").joinpath("not_base64.json")


@pytest.fixture
def json_file_missing_max_temp() -> Path:
    """Return json test file without max temp.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("data").joinpath("missing_required_max_temp.json")


@pytest.fixture
def json_file_missing_min_temp() -> Path:
    """Return json test file without min temp.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("data").joinpath("missing_required_min_temp.json")


@pytest.fixture
def json_file_missing_operation_modes() -> Path:
    """Return json test file without operation modes.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("data").joinpath("missing_required_operation_modes.json")


@pytest.fixture(scope="function")
def runner(request):
    """Pytest runner fixture.

    Arguments:
        request: pytest request

    Returns:
        Click CliRunner object
    """
    return CliRunner()
