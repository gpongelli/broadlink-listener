# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Broadlink device manager."""

import binascii
import time
from typing import Optional

import click
from broadlink import Device, gendevice
from broadlink.const import DEFAULT_PORT, DEFAULT_TIMEOUT
from broadlink.exceptions import ReadError, StorageError


class BroadlinkManager:  # pylint: disable=too-few-public-methods
    """Manager class for Broadlink device."""

    def __init__(self, dev_type: str, ip_addr: str, mac_addr: str):
        """Broadlink Manager.

        Arguments:
            dev_type: Broadlink device type from discover IR command
            ip_addr: Broadlink IP address from discover IR command
            mac_addr: Broadlink MAC address from discover IR command
        """
        self.__dev: Device = gendevice(int(dev_type, 0), (ip_addr, DEFAULT_PORT), mac_addr)
        self.__dev.auth()

    def learn_single_code(self) -> Optional[str]:
        """Process to learn single IR code.

        Returns:
            Optional[str]: str if IR code was listened, None otherwise
        """
        click.echo("Listening...")
        self.__dev.enter_learning()
        start = time.time()
        _ret = None
        while time.time() - start < DEFAULT_TIMEOUT:
            time.sleep(1)
            try:
                data: bytes = self.__dev.check_data()
            except (ReadError, StorageError):
                continue
            else:
                b64_data = binascii.b2a_base64(data, newline=False)
                _ret = b64_data.decode('utf-8')
                break

        return _ret
