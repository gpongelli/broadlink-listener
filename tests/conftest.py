# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Pytest conftest."""

import binascii
import glob
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import pytest
from click.testing import CliRunner


def _remove_tmp_files(file_pattern=r"[a-zA-Z_]*_tmp[_\d]+.json"):
    """Utility method to remove test generated files.

    Arguments:
        file_pattern: regex pattern for files to be removed.
    """
    _pattern = re.compile(file_pattern)
    _previous = glob.glob(os.path.join(Path.cwd().joinpath("tests").joinpath("data"), '*'))
    for _file in _previous:
        if _pattern.match(os.path.basename(_file)):
            os.remove(_file)


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
def json_file_good_data_op_mode() -> Generator:
    """Return json test file with good structure.

    Yields:
        json's path file
    """
    yield Path.cwd().joinpath("tests").joinpath("data").joinpath("good_data_op_mode.json")
    _remove_tmp_files()
    _remove_tmp_files(r"[a-zA-Z_]*_[\d]+_[\d]+.json")


@pytest.fixture
def json_file_good_data_op_fan_mode() -> Generator:
    """Return json test file with good structure.

    Yields:
        json's path file
    """
    yield Path.cwd().joinpath("tests").joinpath("data").joinpath("good_data_op_fan_mode.json")
    _remove_tmp_files()
    _remove_tmp_files(r"[a-zA-Z_]*_[\d]+_[\d]+.json")


@pytest.fixture
def json_file_good_data_op_fan_swing_mode() -> Generator:
    """Return json test file with good structure.

    Yields:
        json's path file
    """
    yield Path.cwd().joinpath("tests").joinpath("data").joinpath("good_data_op_fan_swing_mode.json")
    _remove_tmp_files()
    _remove_tmp_files(r"[a-zA-Z_]*_[\d]+_[\d]+.json")


@pytest.fixture
def json_file_good_data_op_swing_mode() -> Generator:
    """Return json test file with good structure.

    Yields:
        json's path file
    """
    yield Path.cwd().joinpath("tests").joinpath("data").joinpath("good_data_op_swing_mode.json")
    _remove_tmp_files()
    _remove_tmp_files(r"[a-zA-Z_]*_[\d]+_[\d]+.json")


@pytest.fixture
def json_file_partial_dict_op_fan_swing_mode() -> Path:
    """Return json test file with good structure for partial load.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("partial_dicts").joinpath("good_data_op_fan_swing_mode.json")


@pytest.fixture
def json_file_previous_partial_dict_op_fan_swing_mode() -> Path:
    """Return json test file with good structure for partial load.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("partial_dicts").joinpath("good_data_op_fan_swing_mode_tmp_003.json")


@pytest.fixture
def json_file_partial_dict_op_swing_mode() -> Path:
    """Return json test file with good structure for partial load.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("partial_dicts").joinpath("good_data_op_swing_mode.json")


@pytest.fixture
def json_file_last_previous_partial_dict_op_swing_mode() -> Path:
    """Return json test file with good structure for partial load.

    Returns:
        json's path file
    """
    return Path.cwd().joinpath("tests").joinpath("partial_dicts").joinpath("good_data_op_swing_mode_tmp_003.json")


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


def dict_from_json(json_file: Path) -> dict:
    """Obtain json content from file path.

    Arguments:
        json_file: path of json file

    Returns:
        json's content as dict
    """
    with open(str(json_file), "r", encoding='utf-8') as in_file:
        _expected_dict = json.load(in_file)
    return _expected_dict


@dataclass
class ExpectedValues:
    """Test expected values and bytes that generate them."""

    code_inc: bytes
    code_dec: bytes
    code_even: bytes
    code_odd: bytes
    code_upper: bytes
    code_lower: bytes
    code_last: bytes
    code_last_lower: bytes
    expected_inc: str
    expected_dec: str
    expected_even: str
    expected_odd: str
    expected_upper: str
    expected_lower: str
    expected_last: str
    expected_last_lower: str

    @staticmethod
    def _bytes_to_str(code: bytes) -> str:
        b64_data = binascii.b2a_base64(code, newline=False)
        return b64_data.decode('utf-8')

    def __init__(self):
        """Object initialization."""
        self.code_inc = b'12345678'
        self.code_dec = b'87654321'
        self.code_even = b'024681012'
        self.code_odd = b'135791113'
        self.code_upper = b'ABCDEFG'
        self.code_lower = b'abcdefg'
        self.code_last = b'TUVWXYZ'
        self.code_last_lower = b'tuvwxyz'

        self.expected_inc = ExpectedValues._bytes_to_str(self.code_inc)
        self.expected_dec = ExpectedValues._bytes_to_str(self.code_dec)
        self.expected_even = ExpectedValues._bytes_to_str(self.code_even)
        self.expected_odd = ExpectedValues._bytes_to_str(self.code_odd)
        self.expected_upper = ExpectedValues._bytes_to_str(self.code_upper)
        self.expected_lower = ExpectedValues._bytes_to_str(self.code_lower)
        self.expected_last = ExpectedValues._bytes_to_str(self.code_last)
        self.expected_last_lower = ExpectedValues._bytes_to_str(self.code_last_lower)
