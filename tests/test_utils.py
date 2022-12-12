# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Test utils module."""

import logging
import socket
from unittest.mock import Mock, patch

from broadlink_listener.cli_tools.utils import configure_logger, get_local_ip_address


@patch('logging.basicConfig')
def test_logger(patched_log):
    """Testing configure_logger.

    Arguments:
        patched_log: patched basicConfig method
    """
    configure_logger()
    patched_log.assert_called_with(
        level=logging.INFO, format='%(asctime)s [%(levelname)s - %(filename)s:%(lineno)d]    %(message)s', handlers=None
    )

    configure_logger('info')
    patched_log.assert_called_with(
        level=logging.INFO, format='%(asctime)s [%(levelname)s - %(filename)s:%(lineno)d]    %(message)s', handlers=None
    )

    configure_logger('debug')
    patched_log.assert_called_with(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s - %(filename)s:%(lineno)d]    %(message)s',
        handlers=None,
    )

    configure_logger('warning')
    patched_log.assert_called_with(
        level=logging.WARN, format='%(asctime)s [%(levelname)s - %(filename)s:%(lineno)d]    %(message)s', handlers=None
    )

    configure_logger('error')
    patched_log.assert_called_with(
        level=logging.ERROR,
        format='%(asctime)s [%(levelname)s - %(filename)s:%(lineno)d]    %(message)s',
        handlers=None,
    )


@patch('socket.socket.getsockname', Mock(side_effect=TimeoutError()))
def test_get_ip_localhost():
    """Testing get_local_ip_address with localhost address."""
    assert get_local_ip_address() == "127.0.0.1"


@patch('socket.socket.getsockname', Mock(return_value=['192.168.1.150']))
def test_get_ip_real_ip_patched():
    """Testing get_local_ip_address with real mocked address."""
    assert get_local_ip_address() == '192.168.1.150'


def test_get_ip_real_ip():
    """Testing get_local_ip_address with real mocked address."""
    with patch('socket.socket.connect'), patch('socket.socket'), patch(
        'socket.socket.getsockname', Mock(return_value='192.168.1.150')
    ):
        assert socket.socket.getsockname() == '192.168.1.150'
