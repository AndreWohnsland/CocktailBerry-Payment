import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field

import typer
from typer import colors

from src.shared import ENV_PATH


@dataclass
class ConfigItem:
    name: str
    description: str
    default: str = field(default="")


@dataclass
class ConfigSection:
    active: bool = False
    use_docker: bool = False
    supports_docker: bool = False
    setup: Callable = field(default=lambda: print("Setup not implemented"))
    docker_setup: Callable = field(default=lambda: print("Docker setup not implemented"))

    def setup_service(self) -> None:
        """Set up the service based on selected options."""
        if self.use_docker:
            self.docker_setup()
        else:
            self.setup()


def read_env_file() -> dict[str, str]:
    """Read a .env file and return dict of existing values."""
    if not ENV_PATH.exists():
        return {}
    result = {}
    with ENV_PATH.open() as f:
        for read_line in f:
            line = read_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                result[key.strip()] = value.strip()
    return result


def write_env_file(values: dict[str, str]) -> None:
    """Save updated values to .env."""
    with ENV_PATH.open("w") as f:
        for k, v in values.items():
            f.write(f"{k}={v}\n")


def prompt_for_values(items: list[ConfigItem], existing: dict[str, str]) -> dict[str, str]:
    """Show each value, prompt user, require a non-empty value."""
    results: dict[str, str] = {}

    typer.secho("- Settings:", fg=colors.CYAN, bold=True)
    for item in items:
        current = existing.get(item.name, item.default)
        prompt_text = f"{item.description}"
        response = typer.prompt(prompt_text, default=current)
        # if user leaves empty, use current
        if not response:
            response = current
        results[item.name] = response
    return results


def set_user_env_vars(values: dict[str, str]) -> None:
    for k, v in values.items():
        subprocess.run(
            [
                "powershell",
                "-Command",
                f"[Environment]::SetEnvironmentVariable('{k}', '{v}', 'User')",
            ],
            check=True,
        )
