"""Unit tests for Apple Access configuration."""

from pydantic import ValidationError
import pytest


class TestAccessConfig:
    """AccessTCI is a hex value; AccessAuthRequired is 0/1."""

    def test_valid_tci(self) -> None:
        """A six-character hex TCI is accepted."""
        from vtap100.models.access import AccessConfig

        assert AccessConfig(tci="020000").tci == "020000"

    def test_tci_is_uppercased(self) -> None:
        """Hex is normalised to upper case."""
        from vtap100.models.access import AccessConfig

        assert AccessConfig(tci="02ab00").tci == "02AB00"

    def test_non_hex_tci_is_rejected(self) -> None:
        """A non-hex TCI is an error."""
        from vtap100.models.access import AccessConfig

        with pytest.raises(ValidationError):
            AccessConfig(tci="ZZZZZZ")

    def test_odd_length_tci_is_rejected(self) -> None:
        """A TCI is whole bytes."""
        from vtap100.models.access import AccessConfig

        with pytest.raises(ValidationError):
            AccessConfig(tci="02000")

    def test_config_lines(self) -> None:
        """Only the fields that are set produce lines."""
        from vtap100.models.access import AccessConfig

        assert AccessConfig(tci="020000", auth_required=True).to_config_lines() == [
            "AccessTCI=020000",
            "AccessAuthRequired=1",
        ]

    def test_empty_config_produces_no_lines(self) -> None:
        """An Access config with nothing set emits nothing."""
        from vtap100.models.access import AccessConfig

        assert AccessConfig().to_config_lines() == []


class TestAccessCoexistsWithVAS:
    """AccessTCI does not disable the pass sections."""

    def test_vas_smarttap_and_access_in_one_config(self) -> None:
        """All three ecosystems coexist in one running configuration.

        The manufacturer's wording ("the reader will operate in ECP2 mode")
        reads like a mode switch, but production configurations carry VAS,
        Smart Tap and Access together.
        """
        from vtap100.parser import parse

        config = parse(
            "!VTAPconfig\n"
            "VAS2MerchantID=pass.com.example.x\n"
            "ST3CollectorID=12345678\n"
            "AccessTCI=020000\n"
        )
        assert len(config.vas_configs) == 1
        assert len(config.smarttap_configs) == 1
        assert config.access is not None
        assert config.access.tci == "020000"

    def test_access_settings_roundtrip(self) -> None:
        """All three Access settings survive a cycle."""
        from vtap100.roundtrip import compare

        text = "!VTAPconfig\nAccessTCI=02AB40\nAccessAuthRequired=1\nECP2Mode=a\n"
        assert compare(text).is_lossless
