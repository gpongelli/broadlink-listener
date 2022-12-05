# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Module with utility methods."""

import logging
import socket


def configure_logger(loglevel: str = 'info') -> None:
    """Configure logger facility, from clients or server side.

    Args:
        loglevel: level of logging facility
    """
    # configure logging
    _log_level = logging.INFO
    if loglevel.lower() == 'debug':
        _log_level = logging.DEBUG
    elif loglevel.lower() == 'warning':
        _log_level = logging.WARNING
    elif loglevel.lower() == 'error':
        _log_level = logging.ERROR

    logging.basicConfig(
        level=_log_level,
        format='%(asctime)s [%(levelname)s - %(filename)s:%(lineno)d]    %(message)s',
        handlers=None,
    )


def get_local_ip_address():
    """Returns local IP address for main interface."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            _ip = s.getsockname()[0]
        except (TimeoutError, InterruptedError, Exception):
            _ip = '127.0.0.1'
    return _ip
