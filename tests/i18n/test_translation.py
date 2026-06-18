import pytest

from src.backend.i18n import translator


@pytest.mark.parametrize("language", ["en", "de"])
def test_translation_keys_exist(language: str) -> None:
    # load_translations builds the Translations dataclass, which raises if the
    # YAML is missing or has extra keys — so this guards completeness per locale.
    translator.load_translations(language)
