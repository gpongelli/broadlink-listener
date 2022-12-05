# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Module with utility methods."""

import logging


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
