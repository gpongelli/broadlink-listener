# SPDX-FileCopyrightText: 2022 Gabriele Pongelli
#
# SPDX-License-Identifier: MIT

"""Console script for broadlink_listener."""

import inspect
import sys
import types
from pathlib import Path
from typing import cast

import click
from cloup import HelpFormatter, HelpTheme, Style, group, option, option_group

from broadlink_listener import __version__

from .utils import configure_logger, get_local_ip_address

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
    """Discover Broadlink IR.

    Arguments:
        local_ip: IP address of this machine connected to same network Broadlink IR is connected to.
    """


@main.command(help="Generate SmartIR json file from input one")
@click.argument('json_file', type=click.Path(exists=True), required=True)
def generate_smart_ir(json_file: Path):
    """Generate SmartIR json file from input one.

    Arguments:
        json_file: SmartIR json file that contains basic structure of codes to be recorded.
    """


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover  # pylint: disable=no-value-for-parameter

    # local test
    # sys.exit(main(['discover_ir']))
