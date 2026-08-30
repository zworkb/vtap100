"""Tests that the firmware requirements are documented.

A VTAP reader silently ignores settings its firmware does not know. There is no
error, no log line, nothing in the generated config.txt to see — the setting
simply has no effect. This was diagnosed the hard way on a reader running
v2.2.8.2 where DESFire#ReadOffset did nothing, because that setting arrived in
v2.3.0.2.

Without documenting it, the next person spends the same afternoon on it.
"""

from pathlib import Path
import pytest


DOCS = Path(__file__).parent.parent.parent / "docs"

# Setting -> core firmware release that introduced it, per the VTAP release notes.
MINIMUM_FIRMWARE = {
    "DESFire#ReadOffset": "v2.3.0.2",
    "ECP2Mode": "v2.5.3.0",
}


class TestFirmwareRequirementsAreDocumented:
    """The version a setting needs must be findable where the setting is."""

    def test_desfire_page_states_the_readoffset_requirement(self) -> None:
        """Someone reading about ReadOffset must learn it needs v2.3.0.2."""
        text = (DOCS / "configuration" / "desfire.md").read_text(encoding="utf-8")
        assert "v2.3.0.2" in text

    def test_settings_reference_states_both_requirements(self) -> None:
        """The reference table is where people compare settings."""
        text = (DOCS / "configuration" / "settings_reference.md").read_text(encoding="utf-8")
        for version in MINIMUM_FIRMWARE.values():
            assert version in text, f"settings_reference.md does not mention {version}"

    def test_troubleshooting_explains_the_silent_failure(self) -> None:
        """The symptom is silence, so the symptom needs its own entry."""
        text = (DOCS / "troubleshooting.md").read_text(encoding="utf-8")
        assert "BOOT.TXT" in text, "troubleshooting does not say how to check the version"
        assert "v2.3.0.2" in text

    @pytest.mark.parametrize("setting", sorted(MINIMUM_FIRMWARE))
    def test_setting_is_named_alongside_its_version(self, setting: str) -> None:
        """A version number without its setting helps nobody."""
        text = (DOCS / "configuration" / "settings_reference.md").read_text(encoding="utf-8")
        assert setting in text, f"settings_reference.md does not mention {setting}"
