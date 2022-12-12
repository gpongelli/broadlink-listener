# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Test Broadlink manager module."""
from unittest.mock import Mock, patch

import broadlink.remote
import pytest
from broadlink import gendevice
from broadlink.const import DEFAULT_PORT

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
        _a = gendevice(0x51DA, ('192.168.1.1', DEFAULT_PORT), '12345678')
        assert issubclass(type(_a), broadlink.remote.rmmini)
        assert hasattr(_a, 'enter_learning')

    @patch('broadlink.device.Device.auth', Mock(return_value=True))
    def test_broadlink_manager_device(self):
        _a = BroadlinkManager('0x51DA', '192.168.1.1', '12345678')
        assert issubclass(type(_a.device), broadlink.remote.rmmini)
        assert hasattr(_a.device, 'enter_learning')
