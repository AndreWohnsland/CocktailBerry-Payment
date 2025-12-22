from dataclasses import dataclass
from pathlib import Path

import yaml

from src.frontend.core.config import config as cfg

TRANSLATION_DIR = Path(__file__).parent / "translations"


@dataclass
class Translations:
    action: str
    adult: str
    amount: str
    balance_no_amount_given: str
    balance_notify_add: str
    balance_update_failed: str
    balance_update: str
    balance_updated: str
    balance_updating: str
    balance: str
    cancel: str
    child: str
    clear: str
    config_description: str
    config_header: str
    config_invalid_value: str
    config_label_api_address: str
    config_label_api_key: str
    config_label_api_port: str
    config_label_default_balance: str
    config_label_full_screen: str
    config_label_language: str
    config_label_native_mode: str
    config_label_nfc_timeout: str
    config_saved: str
    config_value_false: str
    config_value_true: str
    confirm: str
    create_adult_description: str
    create_nfc_creating: str
    create_nfc_saved: str
    create_nfc: str
    created_at: str
    delete: str
    header_create: str
    header_top_up: str
    header_history: str
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
    request_error: str
    tab_config: str
    tab_create: str
    tab_history: str
    tab_manage: str
    tab_top_up: str


def load_translations(lang: str = cfg.language) -> Translations:
    file_path = TRANSLATION_DIR / f"{lang}.yaml"
    if not file_path.exists():
        file_path = TRANSLATION_DIR / "en.yaml"
    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Translations(**data)


# Singleton instance for app-wide use
translations = load_translations()
