# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Console script for broadlink_listener."""

import binascii
import inspect
import json
import logging
import sys
import time
import types
from itertools import product
from pathlib import Path
from typing import Optional, cast

import click
from broadlink import Device, discover, gendevice
from broadlink.const import DEFAULT_BCAST_ADDR, DEFAULT_PORT, DEFAULT_TIMEOUT
from broadlink.exceptions import ReadError, StorageError
from cloup import HelpFormatter, HelpTheme, Style, group, option, option_group

from broadlink_listener import __version__
from broadlink_listener.cli_tools.utils import configure_logger, get_local_ip_address

formatter_settings = HelpFormatter.settings(
    theme=HelpTheme(
        invoked_command=Style(fg='bright_yellow'),
        heading=Style(fg='bright_white', bold=True),
        constraint=Style(fg='magenta'),
        col1=Style(fg='bright_yellow'),
    )
)


@group(align_option_groups=False, formatter_settings=formatter_settings, no_args_is_help=False)  # type: ignore
@option_group(
    "Generic Options",
    option(
        '-d',
        '--loglevel',
        'loglevel',
        type=click.Choice(["debug", "info", "warning", "error"], case_sensitive=False),
        default="info",
        show_default=True,
        help="set log level",
    ),
)
@click.version_option(__version__)
def main(loglevel: str):
    """Broadlink listener.

    # noqa: DAR101
    """
    _fnc_name = cast(types.FrameType, inspect.currentframe()).f_code.co_name
    _complete_doc = inspect.getdoc(eval(_fnc_name))  # pylint: disable=eval-used  # nosec B307
    _doc = f"{_complete_doc}".split('\n')[0]  # use only doc first row
    _str = f"{_doc[:-1]} - v{__version__}"
    click.echo(f"{_str}")
    click.echo("=" * len(_str))
    click.echo("Broadlink IR codes listener and SmartIR json generator.")

    # ctx.ensure_object(dict)
    # ctx.obj = loglevel
    configure_logger(loglevel)


@main.command(help="Discover Broadlink IR")
@click.argument('local_ip', type=str, default=get_local_ip_address(), required=True)
def discover_ir(local_ip: str):
    """Discover Broadlink IR, code from python-broadlink.

    Arguments:
        local_ip: IP address of this machine connected to same network Broadlink IR is connected to.
    """
    devices = discover(timeout=DEFAULT_TIMEOUT, local_ip_address=local_ip, discover_ip_address=DEFAULT_BCAST_ADDR)
    for device in devices:
        if device.auth():
            click.echo("###########################################")
            click.echo(f"Device Type: {device.type}")
            click.echo(
                f"Broadlink Type: {hex(device.devtype)}\n"
                f"Broadlink IP Address: {device.host[0]} "
                f"Broadlink MAC Address: {''.join(format(x, '02x') for x in device.mac)}"
            )
        else:
            logging.error("Error authenticating with device : %s", device.host)


@main.command(help="Generate SmartIR json file from input one")
@click.argument('json_file', type=click.Path(exists=True), required=True)
@click.argument('dev_type', type=str, required=True)
@click.argument('ip_addr', type=str, required=True)
@click.argument('mac_addr', type=str, required=True)
@click.option('--no-temp-on-mode', '-n', type=str, multiple=True)
@click.option('--no-swing-on-mode', '-s', type=str, multiple=True)
def generate_smart_ir(
    json_file: Path, dev_type: str, ip_addr: str, mac_addr: str, no_temp_on_mode: tuple, no_swing_on_mode: tuple
):  # pylint: disable=too-many-arguments, too-many-locals
    """Generate SmartIR json file from input one.

    Arguments:
        json_file: SmartIR json file that contains basic structure of codes to be recorded.
        dev_type: Broadlink device type from discover IR command
        ip_addr: Broadlink IP address from discover IR command
        mac_addr: Broadlink MAC address from discover IR command
        no_temp_on_mode: option, that can be set multiple times, related to operating mode that have no temperature
                         selection
        no_swing_on_mode: option, that can be set multiple times, related to operating mode that have no swing
                          selection

    Raises:
        UsageError: raised if controller is not Broadlink or no IR signal is learnt during the process
    """
    with open(str(json_file), "r", encoding='utf-8') as in_file:
        smartir_dict = json.load(in_file)

    try:
        if smartir_dict["supportedController"] != "Broadlink":
            logging.error("Controller %s not supported", smartir_dict['supportedController'])
            raise click.exceptions.UsageError(f"Controller {smartir_dict['supportedController']} not supported")

        min_temp = int(smartir_dict["minTemperature"])
        max_temp = int(smartir_dict["maxTemperature"])
        precision_temp = int(smartir_dict.get("precision", 1))
        op_modes = smartir_dict.get("operationModes", [])
        fan_modes = smartir_dict.get("fanModes", [])
        swing_modes = smartir_dict.get("swingModes", [])

    except KeyError as key_err:
        logging.error("missing mandatory field in json file")
        logging.error(key_err)
    else:
        dev = gendevice(int(dev_type, 0), (ip_addr, DEFAULT_PORT), mac_addr)
        dev.auth()

        click.echo("First of all, let's learn OFF command...")
        _countdown()
        _off = _learn_single_code(dev)
        if not _off:
            raise click.exceptions.UsageError("No IR signal learnt for OFF command.")
        smartir_dict["commands"]["off"] = _off

        all_combinations = product(op_modes, fan_modes, swing_modes, range(min_temp, max_temp + 1, precision_temp))
        for combination in all_combinations:
            print(combination)


def _countdown():
    for i in range(5, 0, -1):
        click.echo(i)
        time.sleep(1)


def _learn_single_code(device: Device) -> Optional[str]:
    click.echo("Learning...")
    device.enter_learning()
    start = time.time()
    _ret = None
    while time.time() - start < DEFAULT_TIMEOUT:
        time.sleep(1)
        try:
            data = device.check_data()
        except (ReadError, StorageError):
            continue
        else:
            _learnt = ''.join(format(x, '02x') for x in bytearray(data))
            _decode_hex = codecs.getdecoder("hex_codec")
            b64 = base64.b64encode(_decode_hex(_learnt)[0])
            _ret = b64.decode('utf-8')
            break

    return _ret


if __name__ == "__main__":
    # sys.exit(main())  # pragma: no cover  # pylint: disable=no-value-for-parameter

    # local test
    sys.exit(main(['discover-ir']))
