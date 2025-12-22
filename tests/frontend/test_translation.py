import pytest

from src.frontend.i18n import translator


@pytest.mark.parametrize("language", ["en", "de"])
def test_translation_keys_exist(language: str) -> None:
    translator.load_translations(language)
