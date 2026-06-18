"""Backend translations for user-facing domain-error messages.

Mirrors the frontend translator: one YAML file per language, loaded once into a
``Translations`` dataclass for the language configured by ``LANGUAGE``. A missing
language file falls back to English. Domain errors render their message through
the ``translations`` singleton, so ``str(exc)`` (and therefore both the API detail
and the logs) follow the configured language.
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.backend.core.config import config as cfg

TRANSLATION_DIR = Path(__file__).parent / "translations"


@dataclass
class Translations:
    """Message templates for each domain error. Placeholders are ``str.format`` style."""

    err_balance_below_minimum: str
    err_duplicate_nfc: str
    err_insufficient_balance: str
    err_underage_booking: str
    err_user_not_found: str


def load_translations(lang: str = cfg.language) -> Translations:
    file_path = TRANSLATION_DIR / f"{lang}.yaml"
    if not file_path.exists():
        file_path = TRANSLATION_DIR / "en.yaml"
    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Translations(**data)


# Singleton for app-wide use, loaded for the configured language.
translations = load_translations()
