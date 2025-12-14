import sys
from pathlib import Path

import typer
from typer import colors

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from scripts.helpers import ConfigItem, prompt_for_values, read_env_file, write_env_file

APP = typer.Typer()

# define frontend config items
CONFIG_VARIABLES: dict[str, list[ConfigItem]] = {
    "frontend": [
        ConfigItem("API_KEY", "API key for backend service", default="CocktailBerry-Secret-Change-Me"),
        ConfigItem("API_PORT", "Port for backend service", default="9876"),
        ConfigItem("API_ADDRESS", "Address for backend service", default="http://localhost"),
        ConfigItem("LANGUAGE", "Default language (e.g., en, de)", default="en"),
        ConfigItem("DEFAULT_BALANCE", "Default balance for new users", default="10.0"),
        ConfigItem("NFC_TIMEOUT", "NFC operation timeout in seconds", default="10.0"),
    ],
    "backend": [
        ConfigItem("API_KEY", "API key for backend service", default="CocktailBerry-Secret-Change-Me"),
        ConfigItem("API_PORT", "Port for backend service", default="9876"),
    ],
}


@APP.command()
def setup() -> None:
    """Interactive setup for frontend/backend configuration."""
    # read existing .env
    env = read_env_file()

    services = ["frontend", "backend"]
    number_setups = 0
    typer.secho("Welcome to the CocktailBerry Payment Manager setup!", fg=colors.CYAN, bold=True)
    for service in services:
        set_up = typer.confirm(f"Do you want to configure and setup the {service}?")
        if not set_up:
            continue
        number_setups += 1

        typer.secho(f"\n📌 Configuring {service.capitalize()}", fg=colors.BLUE)
        if service == "backend":
            typer.secho("- Select backend type:", fg=colors.CYAN, bold=True)
            typer.echo("Docker is recommended if you use the default setup and are not on a windows host.")
            backend_mode = typer.prompt("Type 'python' or 'docker'", default="docker").strip().lower()

            while backend_mode not in ("python", "docker"):
                typer.secho("❌ Must be 'python' or 'docker'.", fg=colors.RED)
                backend_mode = typer.prompt("Type 'python' or 'docker'").strip().lower()

        items = CONFIG_VARIABLES[service]
        results = prompt_for_values(items, env)
        env.update(results)
        print("")

    if number_setups == 0:
        typer.secho("No services selected for configuration. Exiting.", fg=colors.YELLOW)
        raise typer.Exit()

    write_env_file(env)
    typer.secho("Configuration complete!", fg=colors.GREEN, bold=True)


if __name__ == "__main__":
    APP()
