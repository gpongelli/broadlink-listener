"""Console script for broadlink_listener."""

import click

from broadlink_listener import __version__


@click.command()
def main():
    """Main entrypoint."""
    _str = f"broadlink-listener v{__version__}"
    click.echo(_str)
    click.echo("=" * len(_str))
    click.echo("Broadlink IR codes listener and SmartIR json generator.")


if __name__ == "__main__":
    main()  # pragma: no cover
