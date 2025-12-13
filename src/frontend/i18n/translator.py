import os
from dataclasses import dataclass
from pathlib import Path

import yaml

TRANSLATION_DIR = Path(__file__).parent / "translations"
LANGUAGE = os.getenv("LANGUAGE", "de")


@dataclass
class Translations:
    adult: str
    balance_notify_add: str
    balance_update: str
    balance_updated: str
    balance_updating: str
    balance: str
    cancel: str
    child: str
    clear: str
    confirm: str
    create_adult_description: str
    create_nfc_creating: str
    create_nfc_saved: str
    create_nfc: str
    delete: str
    header_create: str
    header_top_up: str
    manage_card_deleted: str
    manage_delete_confirm: str
    mange_filter_hint: str
    nfc_card_not_registered: str
    nfc_found: str
    nfc_no_card_detected: str
    nfc_no_card_scanned: str
    nfc_not_found_detail: str
    nfc_not_found: str
    nfc_ready_to_scan: str
    nfc_scan_complete: str
    nfc_scan_hint: str
    nfc_scan: str
    nfc_scanned_card: str
    nfc_scanning_progress: str
    nfc_simulate_hint: str
    nfc_timeout: str
    balance_no_amount_given: str
    tab_create: str
    tab_manage: str
    tab_top_up: str


def load_translations(lang: str = LANGUAGE) -> Translations:
    file_path = TRANSLATION_DIR / f"{lang}.yaml"
    if not file_path.exists():
        file_path = TRANSLATION_DIR / "en.yaml"
    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Translations(**data)


# Singleton instance for app-wide use
translations = load_translations()
