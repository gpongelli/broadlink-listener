# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Test smartir manager module."""

import binascii
import json
from unittest.mock import Mock, patch

import click
import pytest

from broadlink_listener.cli_tools.smartir_manager import BroadlinkManager, SmartIrManager


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

    def test_learning_op_mode(self, json_file_good_data_op_mode):
        """Test dict generation, operationMode only.

        Arguments:
            json_file_good_data_op_mode: json file
        """
        _code_value = b'12345678'
        b64_data = binascii.b2a_base64(_code_value, newline=False)
        _expected = b64_data.decode('utf-8')
        with open(str(json_file_good_data_op_mode), "r", encoding='utf-8') as in_file:
            _expected_dict = json.load(in_file)

        _expect_dict_before_learn = dict(_expected_dict)
        _expect_dict_before_learn['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                '18': '',
                '19': '',
                '20': '',
            },
            'heat': {
                '18': '',
                '19': '',
                '20': '',
            },
        }

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                '18': _expected,
                '19': _expected,
                '20': _expected,
            },
            'heat': {
                '18': _expected,
                '19': _expected,
                '20': _expected,
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('broadlink.remote.rmmini.check_data', Mock(return_value=_code_value)):
            _a = SmartIrManager(json_file_good_data_op_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678'))
            assert _expect_dict_before_learn == _a.smartir_dict

            _a.lear_all()
            assert _expected_dict == _a.smartir_dict

    def test_learning_op_fan_mode(self, json_file_good_data_op_fan_mode):
        """Test dict generation, operationMode and fanMode only.

        Arguments:
            json_file_good_data_op_fan_mode: json file
        """
        _code_value = b'12345678'
        b64_data = binascii.b2a_base64(_code_value, newline=False)
        _expected = b64_data.decode('utf-8')
        with open(str(json_file_good_data_op_fan_mode), "r", encoding='utf-8') as in_file:
            _expected_dict = json.load(in_file)

        _expect_dict_before_learn = dict(_expected_dict)
        _expect_dict_before_learn['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    '18': '',
                    '19': '',
                },
                'high': {
                    '18': '',
                    '19': '',
                },
            },
            'heat': {
                'low': {
                    '18': '',
                    '19': '',
                },
                'high': {
                    '18': '',
                    '19': '',
                },
            },
        }

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    '18': _expected,
                    '19': _expected,
                },
                'high': {
                    '18': _expected,
                    '19': _expected,
                },
            },
            'heat': {
                'low': {
                    '18': _expected,
                    '19': _expected,
                },
                'high': {
                    '18': _expected,
                    '19': _expected,
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('broadlink.remote.rmmini.check_data', Mock(return_value=_code_value)):
            _a = SmartIrManager(json_file_good_data_op_fan_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678'))
            assert _expect_dict_before_learn == _a.smartir_dict

            _a.lear_all()
            assert _expected_dict == _a.smartir_dict

    def test_learning_op_swing_mode(self, json_file_good_data_op_swing_mode):
        """Test dict generation, operationMode and swingMode only.

        Arguments:
            json_file_good_data_op_swing_mode: json file
        """
        _code_value = b'12345678'
        b64_data = binascii.b2a_base64(_code_value, newline=False)
        _expected = b64_data.decode('utf-8')
        with open(str(json_file_good_data_op_swing_mode), "r", encoding='utf-8') as in_file:
            _expected_dict = json.load(in_file)

        _expect_dict_before_learn = dict(_expected_dict)
        _expect_dict_before_learn['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'up': {
                    '18': '',
                    '19': '',
                },
                'down': {
                    '18': '',
                    '19': '',
                },
            },
            'heat': {
                'up': {
                    '18': '',
                    '19': '',
                },
                'down': {
                    '18': '',
                    '19': '',
                },
            },
        }

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'up': {
                    '18': _expected,
                    '19': _expected,
                },
                'down': {
                    '18': _expected,
                    '19': _expected,
                },
            },
            'heat': {
                'up': {
                    '18': _expected,
                    '19': _expected,
                },
                'down': {
                    '18': _expected,
                    '19': _expected,
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('broadlink.remote.rmmini.check_data', Mock(return_value=_code_value)):
            _a = SmartIrManager(
                json_file_good_data_op_swing_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            )
            assert _expect_dict_before_learn == _a.smartir_dict

            _a.lear_all()
            assert _expected_dict == _a.smartir_dict

    def test_learning_op_fan_swing_mode(self, json_file_good_data_op_fan_swing_mode):
        """Test dict generation, all fields.

        Arguments:
            json_file_good_data_op_fan_swing_mode: json file
        """
        _code_value = b'12345678'
        b64_data = binascii.b2a_base64(_code_value, newline=False)
        _expected = b64_data.decode('utf-8')
        with open(str(json_file_good_data_op_fan_swing_mode), "r", encoding='utf-8') as in_file:
            _expected_dict = json.load(in_file)

        _expect_dict_before_learn = dict(_expected_dict)
        _expect_dict_before_learn['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    'up': {
                        '18': '',
                        '19': '',
                    },
                    'down': {
                        '18': '',
                        '19': '',
                    },
                },
                'high': {
                    'up': {
                        '18': '',
                        '19': '',
                    },
                    'down': {
                        '18': '',
                        '19': '',
                    },
                },
            },
            'heat': {
                'low': {
                    'up': {
                        '18': '',
                        '19': '',
                    },
                    'down': {
                        '18': '',
                        '19': '',
                    },
                },
                'high': {
                    'up': {
                        '18': '',
                        '19': '',
                    },
                    'down': {
                        '18': '',
                        '19': '',
                    },
                },
            },
        }

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    'up': {
                        '18': _expected,
                        '19': _expected,
                    },
                    'down': {
                        '18': _expected,
                        '19': _expected,
                    },
                },
                'high': {
                    'up': {
                        '18': _expected,
                        '19': _expected,
                    },
                    'down': {
                        '18': _expected,
                        '19': _expected,
                    },
                },
            },
            'heat': {
                'low': {
                    'up': {
                        '18': _expected,
                        '19': _expected,
                    },
                    'down': {
                        '18': _expected,
                        '19': _expected,
                    },
                },
                'high': {
                    'up': {
                        '18': _expected,
                        '19': _expected,
                    },
                    'down': {
                        '18': _expected,
                        '19': _expected,
                    },
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('broadlink.remote.rmmini.check_data', Mock(return_value=_code_value)):
            _a = SmartIrManager(
                json_file_good_data_op_fan_swing_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            )
            assert _expect_dict_before_learn == _a.smartir_dict

            _a.lear_all()
            assert _expected_dict == _a.smartir_dict
