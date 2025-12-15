import platform
import subprocess
import sys
from pathlib import Path

import typer
from typer import colors

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DOCKER_COMPOSE_FILE = ROOT / "docker-compose.yaml"

sys.path.insert(0, str(SRC))

from scripts.helpers import ENV_FILE, ConfigItem, ConfigSection, prompt_for_values, read_env_file, write_env_file

APP = typer.Typer()

# define frontend config items
CONFIG_VARIABLES: dict[str, list[ConfigItem]] = {
    "frontend": [
        ConfigItem("API_KEY", "API key for backend service", default="CocktailBerry-Secret-Change-Me"),
        ConfigItem("API_PORT", "Port for backend service", default="9876"),
        ConfigItem("API_ADDRESS", "Address for backend service", default="http://localhost"),
        ConfigItem("LANGUAGE", "Default language (e.g., en, de)", default="en"),
        ConfigItem("NATIVE_MODE", "Runs in a app window instead of website, exit on close", default="false"),
        ConfigItem("FULL_SCREEN", "Run natively in full screen mode", default="false"),
        ConfigItem("DEFAULT_BALANCE", "Default balance for new users", default="10.0"),
        ConfigItem("NFC_TIMEOUT", "NFC operation timeout in seconds", default="10.0"),
    ],
    "backend": [
        ConfigItem("API_KEY", "API key for backend service", default="CocktailBerry-Secret-Change-Me"),
        ConfigItem("API_PORT", "Port for backend service", default="9876"),
    ],
}


def _setup_docker_api() -> None:
    docker_cmd = [
        "docker",
        "compose",
        "-f",
        str(DOCKER_COMPOSE_FILE),
        "-p",
        "cocktailberry-payment",
        "--env-file",
        str(ENV_FILE),
        "up",
        "--build",
        "-d",
    ]
    # check if use docker and docker is installed
    typer.secho("🚀 Starting backend service via Docker...", fg=colors.BLUE)
    result = subprocess.run(docker_cmd, check=False)
    if result.returncode != 0:
        typer.secho("❌ Failed to start backend service via Docker.", fg=colors.RED)
        raise typer.Exit(code=1)
    typer.secho("✅ Backend service started via Docker.", fg=colors.GREEN)


def _setup_api() -> None:
    system = platform.system()
    if system == "Linux":
        _setup_linux_service("api", Path.home() / ".config/autostart")
    elif system == "Windows":
        _setup_api_windows()
    else:
        typer.secho(f"❌ Unsupported OS: {system}", fg=colors.RED)
        raise typer.Exit(code=1)


def _setup_gui() -> None:
    system = platform.system()
    if system == "Linux":
        _setup_linux_service("gui", Path.home() / ".local/share/applications")
    elif system == "Windows":
        _setup_gui_windows()
    else:
        typer.secho(f"❌ Unsupported OS: {system}", fg=colors.RED)
        typer.Exit(code=1)


def _setup_linux_service(service_name: str, destination: Path) -> None:
    """Create and install a .desktop file for the given service."""
    destination.mkdir(parents=True, exist_ok=True)
    template = ROOT / f"scripts/cocktailberry-{service_name}.desktop"
    target = destination / f"cocktailberry-{service_name}.desktop"
    target.write_text(template.read_text().replace("%PROJECT_ROOT%", str(ROOT)))
    target.chmod(0o755)


def _setup_gui_windows() -> None:
    ps_script = ROOT / "scripts/create_gui.ps1"
    subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script), str(ROOT)],
        check=True,
    )


def _setup_api_windows() -> None:
    ps_script = ROOT / "scripts/create_api.ps1"
    subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script), str(ROOT)],
        check=True,
    )


@APP.command()
def setup() -> None:
    """Interactive setup for frontend/backend configuration."""
    # read existing .env
    env = read_env_file()

    services = {
        "frontend": ConfigSection(setup=_setup_gui),
        "backend": ConfigSection(supports_docker=True, setup=_setup_api, docker_setup=_setup_docker_api),
    }
    # add cocktail icon
    typer.secho("🍹 Welcome to the CocktailBerry Payment Manager setup!", fg=colors.CYAN, bold=True)
    for service, data in services.items():
        set_up = typer.confirm(f"Do you want to configure and setup the {service}?")
        if not set_up:
            continue
        data.active = True
        typer.secho(f"\n📌 Configuring {service.capitalize()}", fg=colors.BLUE)
        if data.supports_docker:
            typer.secho("- Select run type:", fg=colors.CYAN, bold=True)
            typer.echo("Docker is recommended if you use the default setup and are not on a windows host.")
            backend_mode = typer.prompt("Type 'python' or 'docker'", default="docker").strip().lower()

            while backend_mode not in ("python", "docker"):
                typer.secho("❌ Must be 'python' or 'docker'.", fg=colors.RED)
                backend_mode = typer.prompt("Type 'python' or 'docker'").strip().lower()
            data.use_docker = backend_mode == "docker"

        items = CONFIG_VARIABLES[service]
        results = prompt_for_values(items, env)
        env.update(results)
        print("")

    if all(not data.active for data in services.values()):
        typer.secho("No services selected for configuration. Exiting.", fg=colors.YELLOW)
        raise typer.Exit()

    typer.secho("📦 Setting up services...", fg=colors.BLUE, bold=True)
    typer.secho("Using configuration:", fg=colors.CYAN)
    for k, v in env.items():
        typer.echo(f" - {k}={v}")
    print("")
    write_env_file(env)

    for service, data in services.items():
        if not data.active:
            continue
        typer.secho(f"🔧 Setting up {service}...", fg=colors.BLUE)
        if not typer.confirm(
            "Use auto setup? Choose no if you use the exe (prebuilt file)",
            default=True,
        ):
            continue
        data.setup_service()
        typer.secho(f"✅ {service.capitalize()} setup complete!", fg=colors.GREEN)

    typer.secho("Configuration complete!", fg=colors.GREEN, bold=True)


if __name__ == "__main__":
    APP()
