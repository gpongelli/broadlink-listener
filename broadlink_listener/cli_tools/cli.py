# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Console script for broadlink_listener."""

import inspect
import logging
import sys
import types
from pathlib import Path
from typing import cast

import click
from broadlink import discover
from broadlink.const import DEFAULT_BCAST_ADDR, DEFAULT_TIMEOUT
from cloup import HelpFormatter, HelpTheme, Style, group, option, option_group

from broadlink_listener import __version__
from broadlink_listener.cli_tools.broadlink_manager import BroadlinkManager
from broadlink_listener.cli_tools.smartir_manager import SmartIrManager
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
@click.option('--no-temp-on-mode', '-n', type=str, multiple=True, default=[])
@click.option('--no-swing-on-mode', '-s', type=str, multiple=True, default=[])
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
    """
    broadlink_mng = BroadlinkManager(dev_type, ip_addr, mac_addr)
    smart_ir_mng = SmartIrManager(json_file, broadlink_mng, no_temp_on_mode, no_swing_on_mode)

    smart_ir_mng.learn_off()
    smart_ir_mng.learn_all()
    smart_ir_mng.save_dict()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover  # pylint: disable=no-value-for-parameter

    # local test
    # sys.exit(main(['discover-ir']))
