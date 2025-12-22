import shutil

import typer
from typer import colors

APP = typer.Typer(add_help_option=False)


@APP.callback(invoke_without_command=True)
def entry_point(
    ctx: typer.Context,
    _: bool = typer.Option(None, "--help", "-h", is_eager=True, help="Show this message and exit."),
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    typer.secho("CocktailBerry Payment Manager CLI helper\n", fg=colors.GREEN, bold=True)
    typer.echo("Possible commands:")
    typer.secho("- Interactively setup the application:", fg=colors.BLUE)
    typer.echo("  > uv run -m cocktailberry.setup")
    typer.secho("- Run the API server:", fg=colors.BLUE)
    typer.echo("  > uv run --extra api -m cocktailberry.api")
    typer.secho("- Run the User Interface:", fg=colors.BLUE)
    typer.echo("  > uv run --extra gui --extra nfc -m cocktailberry.gui")

    if shutil.which("uv") is None:
        typer.secho("\n'uv' is not installed.", fg=colors.RED)
        typer.secho("Please install 'uv' to use the CocktailBerry Payment Manager CLI helper properly.", fg=colors.RED)
        typer.echo("See https://docs.astral.sh/uv/getting-started/installation/ for more information.")


if __name__ == "__main__":
    APP()
    APP()
