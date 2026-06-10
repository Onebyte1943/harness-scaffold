"""CLI entry point for harness."""

from __future__ import annotations

import click

from harness import __version__


@click.group()
@click.version_option(version=__version__, prog_name="harness")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Harness — Unified AI agent engineering scaffold for teams."""
    ctx.ensure_object(dict)


def _register_commands() -> None:
    from harness.cli.doctor_cmd import doctor
    from harness.cli.init_cmd import init
    from harness.cli.state_cmd import state

    cli.add_command(init)
    cli.add_command(doctor)
    cli.add_command(state)


_register_commands()
