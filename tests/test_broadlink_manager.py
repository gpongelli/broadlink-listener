# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Test Broadlink manager module."""
import binascii
from unittest.mock import Mock, patch

import broadlink.remote
import pytest
from broadlink import gendevice
from broadlink.const import DEFAULT_PORT
from broadlink.exceptions import ReadError

from broadlink_listener.cli_tools.broadlink_manager import BroadlinkManager


class TestBroadlinkManager:
    """Broadlink manager test class."""

    @patch('broadlink.device.Device.auth', Mock(return_value=True))
    @patch('broadlink.gendevice')
    def test_init(self, patched_auth):
        """Test initialization.

        Arguments:
            patched_auth: patched version of broadlink Device's auth method.
        """
        _ = BroadlinkManager('0x1234', '192.168.1.1', '12345678')

        with pytest.raises(ValueError):
            _ = BroadlinkManager('0x1234', '192.168.1.1', '1234567ssss8')

        with pytest.raises(ValueError):
            _ = BroadlinkManager('abcs', '192.168.1.1', '12345678')

    def test_rmmini_device(self):
        """Test rmmini device creation with gendevice."""
        _a = gendevice(0x51DA, ('192.168.1.1', DEFAULT_PORT), '12345678')
        assert issubclass(type(_a), broadlink.remote.rmmini)
        assert hasattr(_a, 'enter_learning')

    @patch('broadlink.device.Device.auth', Mock(return_value=True))
    def test_broadlink_manager_device(self):
        """Test rmmini device creation with BroadlinkManager."""
        _a = BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
        assert issubclass(type(_a.device), broadlink.remote.rmmini)
        assert hasattr(_a.device, 'enter_learning')

    def test_learn_code(self):
        """Test rmmini device learn mode."""
        _code_value = b'12345678'
        b64_data = binascii.b2a_base64(_code_value, newline=False)
        _expected = b64_data.decode('utf-8')

        with patch('broadlink.remote.rmmini.enter_learning'), patch(
            'broadlink.device.Device.auth', Mock(return_value=True)
        ), patch('broadlink.remote.rmmini.check_data', Mock(return_value=_code_value)):
            _a = BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            _code = _a.learn_single_code()
            assert _expected == _code

    def test_learn_code_exception(self):
        """Test rmmini device learn mode, exception case will retrieve None ."""
        _expected = None

        with patch('time.sleep'), patch('broadlink_listener.cli_tools.broadlink_manager.DEFAULT_TIMEOUT', 1), patch(
            'broadlink.remote.rmmini.enter_learning'
        ), patch('broadlink.device.Device.auth', Mock(return_value=True)), patch(
            'broadlink.remote.rmmini.check_data', Mock(side_effect=ReadError(-10))
        ):

            _a = BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
            _code = _a.learn_single_code()

            assert _expected == _code
