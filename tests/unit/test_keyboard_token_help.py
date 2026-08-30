"""Tests for the KBPrefix/KBPostfix substitution token documentation.

The help texts described `$t` as a timestamp and invented a `$d` date token.
`$t` is in fact the pass type, which is the one mechanism the reader offers for
telling Apple VAS, Google Smart Tap and Apple Access apart in the output — so
the wrong description does not merely mislead, it hides the feature.

Documented tokens (Keyboard/barcode emulation settings):
    $s  VTAP serial number
    $t  pass type character
    $n  merchant/collector index digit plus key slot digit
    $u  UID as 8, 14 or 16 hex ASCII digits
    $$t literal "$t"
"""

from pathlib import Path
import pytest
import yaml


HELP_DIR = Path(__file__).parent.parent.parent / "src" / "vtap100" / "tui" / "help"
I18N_DIR = Path(__file__).parent.parent.parent / "src" / "vtap100" / "tui" / "i18n" / "translations"

LANGUAGES = ["de", "en"]

# Tokens the manufacturer does not document. A help text offering these sends
# the user looking for behaviour the reader does not have.
INVENTED_TOKENS = ["$d"]

# Wordings that describe $t as something it is not.
WRONG_DESCRIPTIONS = ["timestamp", "zeitstempel", "sequence number", "sequenznummer"]


def _keyboard_help(language: str) -> str:
    """Return the raw keyboard help text for a language."""
    return (HELP_DIR / language / "keyboard.yaml").read_text(encoding="utf-8")


def _translations(language: str) -> str:
    """Return the raw translation file for a language."""
    return (I18N_DIR / f"{language}.yaml").read_text(encoding="utf-8")


class TestTokensAreDescribedCorrectly:
    """The token table must match the manufacturer documentation."""

    @pytest.mark.parametrize("language", LANGUAGES)
    def test_help_does_not_call_the_token_a_timestamp(self, language: str) -> None:
        """$t is the pass type, not a timestamp or a sequence number."""
        text = _keyboard_help(language).lower()
        for wrong in WRONG_DESCRIPTIONS:
            assert wrong not in text, f"{language} keyboard help still says {wrong!r}"

    @pytest.mark.parametrize("language", LANGUAGES)
    def test_translations_do_not_call_the_token_a_timestamp(self, language: str) -> None:
        """The same wording appears in the translation files."""
        text = _translations(language).lower()
        for wrong in WRONG_DESCRIPTIONS:
            assert wrong not in text, f"{language}.yaml still says {wrong!r}"

    @pytest.mark.parametrize("language", LANGUAGES)
    def test_help_offers_no_invented_tokens(self, language: str) -> None:
        """A token the reader does not implement must not be advertised."""
        text = _keyboard_help(language)
        for token in INVENTED_TOKENS:
            assert token not in text, f"{language} keyboard help offers undocumented {token}"

    @pytest.mark.parametrize("language", LANGUAGES)
    def test_help_documents_the_real_tokens(self, language: str) -> None:
        """$u and $s exist and are what makes per-source output possible."""
        text = _keyboard_help(language)
        for token in ["$t", "$n", "$u", "$s"]:
            assert token in text, f"{language} keyboard help does not mention {token}"

    @pytest.mark.parametrize("language", LANGUAGES)
    def test_help_names_the_pass_type_characters(self, language: str) -> None:
        """Knowing $t exists is useless without knowing what it expands to."""
        text = _keyboard_help(language)
        for marker in ["Apple VAS", "Google"]:
            assert marker in text, f"{language} keyboard help does not name {marker}"

    @pytest.mark.parametrize("language", LANGUAGES)
    def test_help_yaml_stays_valid(self, language: str) -> None:
        """The file must still parse after editing."""
        data = yaml.safe_load(_keyboard_help(language))
        assert "fields" in data
        assert "prefix" in data["fields"]
        assert "postfix" in data["fields"]


class TestDocumentationIsConsistent:
    """The prose documentation must not contradict the help texts."""

    def test_keyboard_md_does_not_call_the_token_a_timestamp(self) -> None:
        """docs/configuration/keyboard.md carried the same error twice."""
        path = Path(__file__).parent.parent.parent / "docs" / "configuration" / "keyboard.md"
        text = path.read_text(encoding="utf-8").lower()
        assert "timestamp" not in text

    def test_api_md_does_not_call_the_token_a_timestamp(self) -> None:
        """docs/api.md repeated it in a copy-pasteable example."""
        path = Path(__file__).parent.parent.parent / "docs" / "api.md"
        text = path.read_text(encoding="utf-8").lower()
        assert "timestamp" not in text
