# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Test smartir manager module."""

from itertools import cycle
from unittest.mock import Mock, patch

import click
import pytest
from freezegun import freeze_time

from broadlink_listener.cli_tools.smartir_manager import BroadlinkManager, SmartIrManager
from tests.conftest import ExpectedValues, dict_from_json


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
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_good_data_op_mode)

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
                '18': _expected_values.expected_inc,
                '19': _expected_values.expected_dec,
                '20': _expected_values.expected_odd,
            },
            'heat': {
                '18': _expected_values.expected_even,
                '19': _expected_values.expected_lower,
                '20': _expected_values.expected_upper,
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(json_file_good_data_op_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678'))
            assert _expect_dict_before_learn == _a.smartir_dict

            _a.learn_all()
            assert _expected_dict == _a.smartir_dict

    def test_learning_op_fan_mode(self, json_file_good_data_op_fan_mode):
        """Test dict generation, operationMode and fanMode only.

        Arguments:
            json_file_good_data_op_fan_mode: json file
        """
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_good_data_op_fan_mode)

        _expect_dict_before_learn = dict(_expected_dict)
        _expect_dict_before_learn['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    '18': '',
                    '19': '',
                    '20': '',
                },
                'high': {
                    '18': '',
                    '19': '',
                    '20': '',
                },
            },
            'heat': {
                'low': {
                    '18': '',
                    '19': '',
                    '20': '',
                },
                'high': {
                    '18': '',
                    '19': '',
                    '20': '',
                },
            },
        }

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    '18': _expected_values.expected_inc,
                    '19': _expected_values.expected_dec,
                    '20': _expected_values.expected_odd,
                },
                'high': {
                    '18': _expected_values.expected_even,
                    '19': _expected_values.expected_lower,
                    '20': _expected_values.expected_upper,
                },
            },
            'heat': {
                'low': {
                    '18': _expected_values.expected_last,
                    '19': _expected_values.expected_last_lower,
                    '20': _expected_values.expected_inc,
                },
                'high': {
                    '18': _expected_values.expected_dec,
                    '19': _expected_values.expected_odd,
                    '20': _expected_values.expected_even,
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                        _expected_values.code_last,
                        _expected_values.code_last_lower,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(json_file_good_data_op_fan_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678'))
            assert _expect_dict_before_learn == _a.smartir_dict

            _a.learn_all()
            assert _expected_dict == _a.smartir_dict

    def test_learning_op_swing_mode(self, json_file_good_data_op_swing_mode):
        """Test dict generation, operationMode and swingMode only.

        Arguments:
            json_file_good_data_op_swing_mode: json file
        """
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_good_data_op_swing_mode)

        _expect_dict_before_learn = dict(_expected_dict)
        _expect_dict_before_learn['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'up': {
                    '18': '',
                    '19': '',
                    '20': '',
                },
                'down': {
                    '18': '',
                    '19': '',
                    '20': '',
                },
            },
            'heat': {
                'up': {
                    '18': '',
                    '19': '',
                    '20': '',
                },
                'down': {
                    '18': '',
                    '19': '',
                    '20': '',
                },
            },
        }

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'up': {
                    '18': _expected_values.expected_inc,
                    '19': _expected_values.expected_dec,
                    '20': _expected_values.expected_odd,
                },
                'down': {
                    '18': _expected_values.expected_even,
                    '19': _expected_values.expected_lower,
                    '20': _expected_values.expected_upper,
                },
            },
            'heat': {
                'up': {
                    '18': _expected_values.expected_last,
                    '19': _expected_values.expected_last_lower,
                    '20': _expected_values.expected_inc,
                },
                'down': {
                    '18': _expected_values.expected_dec,
                    '19': _expected_values.expected_odd,
                    '20': _expected_values.expected_even,
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                        _expected_values.code_last,
                        _expected_values.code_last_lower,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(
                json_file_good_data_op_swing_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            )
            assert _expect_dict_before_learn == _a.smartir_dict

            _a.learn_all()
            assert _expected_dict == _a.smartir_dict

    def test_learning_op_fan_swing_mode(self, json_file_good_data_op_fan_swing_mode):
        """Test dict generation, all fields.

        Arguments:
            json_file_good_data_op_fan_swing_mode: json file
        """
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_good_data_op_fan_swing_mode)

        _expect_dict_before_learn = dict(_expected_dict)
        _expect_dict_before_learn['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    'up': {
                        '18': '',
                        '19': '',
                        '20': '',
                    },
                    'down': {
                        '18': '',
                        '19': '',
                        '20': '',
                    },
                },
                'high': {
                    'up': {
                        '18': '',
                        '19': '',
                        '20': '',
                    },
                    'down': {
                        '18': '',
                        '19': '',
                        '20': '',
                    },
                },
            },
            'heat': {
                'low': {
                    'up': {
                        '18': '',
                        '19': '',
                        '20': '',
                    },
                    'down': {
                        '18': '',
                        '19': '',
                        '20': '',
                    },
                },
                'high': {
                    'up': {
                        '18': '',
                        '19': '',
                        '20': '',
                    },
                    'down': {
                        '18': '',
                        '19': '',
                        '20': '',
                    },
                },
            },
        }

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    'up': {
                        '18': _expected_values.expected_inc,
                        '19': _expected_values.expected_dec,
                        '20': _expected_values.expected_odd,
                    },
                    'down': {
                        '18': _expected_values.expected_even,
                        '19': _expected_values.expected_lower,
                        '20': _expected_values.expected_upper,
                    },
                },
                'high': {
                    'up': {
                        '18': _expected_values.expected_last,
                        '19': _expected_values.expected_last_lower,
                        '20': _expected_values.expected_inc,
                    },
                    'down': {
                        '18': _expected_values.expected_dec,
                        '19': _expected_values.expected_odd,
                        '20': _expected_values.expected_even,
                    },
                },
            },
            'heat': {
                'low': {
                    'up': {
                        '18': _expected_values.expected_lower,
                        '19': _expected_values.expected_upper,
                        '20': _expected_values.expected_last,
                    },
                    'down': {
                        '18': _expected_values.expected_last_lower,
                        '19': _expected_values.expected_inc,
                        '20': _expected_values.expected_dec,
                    },
                },
                'high': {
                    'up': {
                        '18': _expected_values.expected_odd,
                        '19': _expected_values.expected_even,
                        '20': _expected_values.expected_lower,
                    },
                    'down': {
                        '18': _expected_values.expected_upper,
                        '19': _expected_values.expected_last,
                        '20': _expected_values.expected_last_lower,
                    },
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                        _expected_values.code_last,
                        _expected_values.code_last_lower,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(
                json_file_good_data_op_fan_swing_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            )
            assert _expect_dict_before_learn == _a.smartir_dict

            _a.learn_all()
            assert _expected_dict == _a.smartir_dict

    def test_partial_op_fan_swing_mode(
        self, json_file_partial_dict_op_fan_swing_mode, json_file_previous_partial_dict_op_fan_swing_mode
    ):
        """Test dict generation, all fields.

        Arguments:
            json_file_partial_dict_op_fan_swing_mode: json file
            json_file_previous_partial_dict_op_fan_swing_mode: json file with partial IR saved
        """
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_previous_partial_dict_op_fan_swing_mode)
        _source_dict = dict_from_json(json_file_partial_dict_op_fan_swing_mode)

        _expected_dict.update({'off': _source_dict['commands']['off']})

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                        _expected_values.code_last,
                        _expected_values.code_last_lower,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(
                json_file_partial_dict_op_fan_swing_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            )
            assert _a.smartir_dict['commands'] == _expected_dict
            assert _a.partial_inc == 3

    def test_partial_op_swing_mode_multiple_files(
        self, json_file_partial_dict_op_swing_mode, json_file_last_previous_partial_dict_op_swing_mode
    ):
        """Test dict generation, all fields.

        Arguments:
            json_file_partial_dict_op_swing_mode: json file
            json_file_last_previous_partial_dict_op_swing_mode: last json file with partial IR saved
        """
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_last_previous_partial_dict_op_swing_mode)
        _source_dict = dict_from_json(json_file_partial_dict_op_swing_mode)

        _expected_dict.update({'off': _source_dict['commands']['off']})

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                        _expected_values.code_last,
                        _expected_values.code_last_lower,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(
                json_file_partial_dict_op_swing_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            )
            assert _a.smartir_dict['commands'] == _expected_dict
            assert _a.partial_inc == 3

    def test_skip_temp(self, json_file_good_data_op_fan_swing_mode):
        """Test dict generation, all fields.

        Arguments:
            json_file_good_data_op_fan_swing_mode: json file
        """
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_good_data_op_fan_swing_mode)

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    'up': {
                        '18': _expected_values.expected_inc,
                        '19': _expected_values.expected_dec,
                        '20': _expected_values.expected_odd,
                    },
                    'down': {
                        '18': _expected_values.expected_even,
                        '19': _expected_values.expected_lower,
                        '20': _expected_values.expected_upper,
                    },
                },
                'high': {
                    'up': {
                        '18': _expected_values.expected_last,
                        '19': _expected_values.expected_last_lower,
                        '20': _expected_values.expected_inc,
                    },
                    'down': {
                        '18': _expected_values.expected_dec,
                        '19': _expected_values.expected_odd,
                        '20': _expected_values.expected_even,
                    },
                },
            },
            'heat': {
                'low': {
                    'up': {
                        '18': _expected_values.expected_lower,
                        '19': _expected_values.expected_lower,
                        '20': _expected_values.expected_lower,
                    },
                    'down': {
                        '18': _expected_values.expected_upper,
                        '19': _expected_values.expected_upper,
                        '20': _expected_values.expected_upper,
                    },
                },
                'high': {
                    'up': {
                        '18': _expected_values.expected_last,
                        '19': _expected_values.expected_last,
                        '20': _expected_values.expected_last,
                    },
                    'down': {
                        '18': _expected_values.expected_last_lower,
                        '19': _expected_values.expected_last_lower,
                        '20': _expected_values.expected_last_lower,
                    },
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                        _expected_values.code_last,
                        _expected_values.code_last_lower,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(
                json_file_good_data_op_fan_swing_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678'), ('heat',)
            )

            _a.learn_all()
            assert _expected_dict == _a.smartir_dict

    def test_skip_swing(self, json_file_good_data_op_fan_swing_mode):
        """Test dict generation, all fields.

        Arguments:
            json_file_good_data_op_fan_swing_mode: json file
        """
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_good_data_op_fan_swing_mode)

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'low': {
                    'up': {
                        '18': _expected_values.expected_inc,
                        '19': _expected_values.expected_dec,
                        '20': _expected_values.expected_odd,
                    },
                    'down': {
                        '18': _expected_values.expected_even,
                        '19': _expected_values.expected_lower,
                        '20': _expected_values.expected_upper,
                    },
                },
                'high': {
                    'up': {
                        '18': _expected_values.expected_last,
                        '19': _expected_values.expected_last_lower,
                        '20': _expected_values.expected_inc,
                    },
                    'down': {
                        '18': _expected_values.expected_dec,
                        '19': _expected_values.expected_odd,
                        '20': _expected_values.expected_even,
                    },
                },
            },
            'heat': {
                'low': {
                    'up': {
                        '18': _expected_values.expected_lower,
                        '19': _expected_values.expected_upper,
                        '20': _expected_values.expected_last,
                    },
                    'down': {
                        '18': _expected_values.expected_lower,
                        '19': _expected_values.expected_upper,
                        '20': _expected_values.expected_last,
                    },
                },
                'high': {
                    'up': {
                        '18': _expected_values.expected_last_lower,
                        '19': _expected_values.expected_inc,
                        '20': _expected_values.expected_dec,
                    },
                    'down': {
                        '18': _expected_values.expected_last_lower,
                        '19': _expected_values.expected_inc,
                        '20': _expected_values.expected_dec,
                    },
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                        _expected_values.code_last,
                        _expected_values.code_last_lower,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(
                json_file_good_data_op_fan_swing_mode,
                BroadlinkManager('0x51DA', '192.168.1.1', '12345678'),
                (),
                ('heat',),
            )

            _a.learn_all()
            assert _expected_dict == _a.smartir_dict

    def test_skip_swing_no_fan_mode(self, json_file_good_data_op_swing_mode):
        """Test dict generation, all fields.

        Arguments:
            json_file_good_data_op_swing_mode: json file
        """
        _expected_values = ExpectedValues()
        _expected_dict = dict_from_json(json_file_good_data_op_swing_mode)

        _expected_dict['commands'] = {
            'off': _expected_dict['commands']['off'],
            'cool': {
                'up': {
                    '18': _expected_values.expected_inc,
                    '19': _expected_values.expected_dec,
                    '20': _expected_values.expected_odd,
                },
                'down': {
                    '18': _expected_values.expected_even,
                    '19': _expected_values.expected_lower,
                    '20': _expected_values.expected_upper,
                },
            },
            'heat': {
                'up': {
                    '18': _expected_values.expected_last,
                    '19': _expected_values.expected_last_lower,
                    '20': _expected_values.expected_inc,
                },
                'down': {
                    '18': _expected_values.expected_last,
                    '19': _expected_values.expected_last_lower,
                    '20': _expected_values.expected_inc,
                },
            },
        }

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink.remote.rmmini.check_data',
            Mock(
                side_effect=cycle(
                    [
                        _expected_values.code_inc,
                        _expected_values.code_dec,
                        _expected_values.code_odd,
                        _expected_values.code_even,
                        _expected_values.code_lower,
                        _expected_values.code_upper,
                        _expected_values.code_last,
                        _expected_values.code_last_lower,
                    ]
                )
            ),
        ):
            _a = SmartIrManager(
                json_file_good_data_op_swing_mode,
                BroadlinkManager('0x51DA', '192.168.1.1', '12345678'),
                (),
                ('heat',),
            )

            _a.learn_all()
            assert _expected_dict == _a.smartir_dict

    def test_skip_swing_cli_param(self, json_file_good_data_op_fan_mode):
        """Test dict generation, all fields.

        Arguments:
            json_file_good_data_op_fan_mode: json file without swing
        """
        with patch('broadlink.device.Device.auth', Mock(return_value=True)):
            with pytest.raises(click.exceptions.UsageError):
                _ = SmartIrManager(
                    json_file_good_data_op_fan_mode,
                    BroadlinkManager('0x51DA', '192.168.1.1', '12345678'),
                    (),
                    ('heat',),
                )

    def test_mode_not_present_from_swing(self, json_file_good_data_op_fan_swing_mode):
        """Test dict generation, all fields.

        Arguments:
            json_file_good_data_op_fan_swing_mode: json file
        """
        with patch('broadlink.device.Device.auth', Mock(return_value=True)):
            with pytest.raises(click.exceptions.UsageError):
                _ = SmartIrManager(
                    json_file_good_data_op_fan_swing_mode,
                    BroadlinkManager('0x51DA', '192.168.1.1', '12345678'),
                    (),
                    ('hesat',),
                )

    def test_mode_not_present_from_temp(self, json_file_good_data_op_fan_swing_mode):
        """Test dict generation, all fields.

        Arguments:
            json_file_good_data_op_fan_swing_mode: json file
        """
        with patch('broadlink.device.Device.auth', Mock(return_value=True)):
            with pytest.raises(click.exceptions.UsageError):
                _ = SmartIrManager(
                    json_file_good_data_op_fan_swing_mode,
                    BroadlinkManager('0x51DA', '192.168.1.1', '12345678'),
                    ('hesat',),
                    (),
                )

    def test_no_code(self, json_file_good_data_op_mode):
        """Test dict generation, operationMode only.

        Arguments:
            json_file_good_data_op_mode: json file
        """
        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'), patch(
            'broadlink_listener.cli_tools.broadlink_manager.BroadlinkManager.learn_single_code', Mock(return_value=None)
        ):
            with pytest.raises(click.exceptions.UsageError):
                _a = SmartIrManager(json_file_good_data_op_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678'))
                _a.learn_all()

            with pytest.raises(click.exceptions.UsageError):
                _a = SmartIrManager(json_file_good_data_op_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678'))
                _a.learn_off()

    @freeze_time("2023-02-10 12:10:30")
    def test_handle_signal(self, json_file_good_data_op_fan_swing_mode, capsys):
        """Test handle keyboard interrupt.

        Arguments:
            json_file_good_data_op_fan_swing_mode: json file
            capsys: pytest mock to capture stdout
        """
        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('time.sleep'), patch('builtins.input'):
            _a = SmartIrManager(
                json_file_good_data_op_fan_swing_mode, BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            )
            _a.save_dict()

            captured = capsys.readouterr()
            assert 'good_data_op_fan_swing_mode_20230210_121030.json' in captured.out
