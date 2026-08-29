"""Unit tests for Apple VAS configuration model.

TDD Red Phase: These tests define the expected behavior of the AppleVASConfig model.
Tests should fail until the implementation is complete.
"""

from pydantic import ValidationError
import pytest


class TestAppleVASConfig:
    """Tests for AppleVASConfig model."""

    def test_vas_config_requires_merchant_id(self) -> None:
        """VAS config must have a merchant_id - it's a required field."""
        from vtap100.models.vas import AppleVASConfig

        with pytest.raises(ValidationError):
            AppleVASConfig(key_slot=1)  # type: ignore[call-arg]

    def test_vas_config_valid_minimal(self) -> None:
        """Valid VAS config with merchant_id and key_slot should be created."""
        from vtap100.models.vas import AppleVASConfig

        # key_slot is now required (1-6), no longer has default
        config = AppleVASConfig(merchant_id="pass.com.example.test", key_slot=1)
        assert config.merchant_id == "pass.com.example.test"
        assert config.key_slot == 1

    def test_vas_config_key_slot_is_optional(self) -> None:
        """key_slot may be omitted.

        The manufacturer documents "=0 or omitted (default), all available keys
        will be compared with the 4 byte hash of the public key for the data".
        """
        from vtap100.models.vas import AppleVASConfig

        assert AppleVASConfig(merchant_id="pass.com.example.test").key_slot is None

    def test_vas_config_key_slot_zero_means_auto(self) -> None:
        """Key slot 0 selects the key automatically and is valid."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(
            merchant_id="pass.com.example.test",
            key_slot=0,
        )
        assert config.key_slot == 0

    def test_vas_config_valid_with_key_slot(self) -> None:
        """Valid VAS config with merchant_id and key_slot."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(
            merchant_id="pass.com.example.test",
            key_slot=1,
        )
        assert config.merchant_id == "pass.com.example.test"
        assert config.key_slot == 1

    def test_vas_config_valid_with_all_fields(self) -> None:
        """Valid VAS config with all optional fields."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(
            merchant_id="pass.com.example.test",
            key_slot=2,
            merchant_url="https://example.com/pass",
        )
        assert config.merchant_id == "pass.com.example.test"
        assert config.key_slot == 2
        assert config.merchant_url == "https://example.com/pass"

    def test_vas_config_merchant_id_must_start_with_pass(self) -> None:
        """Merchant ID must start with 'pass.' prefix."""
        from vtap100.models.vas import AppleVASConfig

        with pytest.raises(ValidationError) as exc_info:
            AppleVASConfig(merchant_id="com.example.test")

        assert "pass." in str(exc_info.value).lower()

    def test_vas_config_merchant_id_empty_string_invalid(self) -> None:
        """Empty string is not a valid merchant_id."""
        from vtap100.models.vas import AppleVASConfig

        with pytest.raises(ValidationError):
            AppleVASConfig(merchant_id="")

    def test_vas_config_key_slot_valid_range(self) -> None:
        """Key slot must be between 1 and 6 (0 is no longer valid)."""
        from vtap100.models.vas import AppleVASConfig

        # Valid slots are now 1-6 only
        for slot in range(1, 7):  # 1-6
            config = AppleVASConfig(
                merchant_id="pass.com.example.test",
                key_slot=slot,
            )
            assert config.key_slot == slot

    def test_vas_config_key_slot_invalid_negative(self) -> None:
        """Negative key slot should be invalid."""
        from vtap100.models.vas import AppleVASConfig

        with pytest.raises(ValidationError):
            AppleVASConfig(
                merchant_id="pass.com.example.test",
                key_slot=-1,
            )

    def test_vas_config_key_slot_invalid_too_high(self) -> None:
        """Key slot > 6 should be invalid."""
        from vtap100.models.vas import AppleVASConfig

        with pytest.raises(ValidationError):
            AppleVASConfig(
                merchant_id="pass.com.example.test",
                key_slot=7,
            )

    def test_vas_config_merchant_url_optional(self) -> None:
        """Merchant URL should be optional and default to None."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(merchant_id="pass.com.example.test", key_slot=1)
        assert config.merchant_url is None


class TestAppleVASConfigOutput:
    """Tests for AppleVASConfig config.txt output generation."""

    def test_to_config_lines_always_includes_key_slot(self) -> None:
        """Config should always generate both MerchantID and KeySlot lines."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(merchant_id="pass.com.example.test", key_slot=1)
        lines = config.to_config_lines(slot_number=1)

        assert "VAS1MerchantID=pass.com.example.test" in lines
        # KeySlot is now always output (required for reader to work)
        assert "VAS1KeySlot=1" in lines

    def test_to_config_lines_with_key_slot(self) -> None:
        """Config with key_slot should include KeySlot line."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(
            merchant_id="pass.com.example.test",
            key_slot=1,
        )
        lines = config.to_config_lines(slot_number=1)

        assert "VAS1MerchantID=pass.com.example.test" in lines
        assert "VAS1KeySlot=1" in lines

    def test_to_config_lines_with_merchant_url(self) -> None:
        """Config with merchant_url should include URL line."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(
            merchant_id="pass.com.example.test",
            key_slot=2,
            merchant_url="https://example.com/pass",
        )
        lines = config.to_config_lines(slot_number=1)

        assert "VAS1MerchantID=pass.com.example.test" in lines
        assert "VAS1KeySlot=2" in lines
        assert "VAS1MerchantURL=https://example.com/pass" in lines

    def test_to_config_lines_different_slot_numbers(self) -> None:
        """Config lines should use correct slot number prefix."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(
            merchant_id="pass.com.example.test",
            key_slot=3,
        )

        # Test different slot numbers
        for slot_num in range(1, 7):
            lines = config.to_config_lines(slot_number=slot_num)
            assert f"VAS{slot_num}MerchantID=pass.com.example.test" in lines
            assert f"VAS{slot_num}KeySlot=3" in lines

    def test_to_config_lines_returns_list(self) -> None:
        """to_config_lines should return a list of strings."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(merchant_id="pass.com.example.test", key_slot=1)
        lines = config.to_config_lines(slot_number=1)

        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)


class TestVASDefaultPassesEnabled:
    """Tests for VASDefaultPassesEnabled setting."""

    def test_default_passes_enabled_default(self) -> None:
        """Default should be all passes enabled (1-6)."""
        from vtap100.models.vas import VASDefaultPassesEnabled

        config = VASDefaultPassesEnabled()
        assert config.enabled_passes == [1, 2, 3, 4, 5, 6]

    def test_default_passes_enabled_custom(self) -> None:
        """Should accept custom list of enabled passes."""
        from vtap100.models.vas import VASDefaultPassesEnabled

        config = VASDefaultPassesEnabled(enabled_passes=[1, 3, 5])
        assert config.enabled_passes == [1, 3, 5]

    def test_default_passes_enabled_single(self) -> None:
        """Should accept single pass enabled."""
        from vtap100.models.vas import VASDefaultPassesEnabled

        config = VASDefaultPassesEnabled(enabled_passes=[2])
        assert config.enabled_passes == [2]

    def test_default_passes_enabled_to_config_line(self) -> None:
        """Should generate correct config line."""
        from vtap100.models.vas import VASDefaultPassesEnabled

        config = VASDefaultPassesEnabled(enabled_passes=[1, 3, 5])
        line = config.to_config_line()
        assert line == "VASDefaultPassesEnabled=1,3,5"

    def test_default_passes_enabled_invalid_pass_number(self) -> None:
        """Pass numbers must be between 1 and 6."""
        from vtap100.models.vas import VASDefaultPassesEnabled

        with pytest.raises(ValidationError):
            VASDefaultPassesEnabled(enabled_passes=[0, 1, 2])

        with pytest.raises(ValidationError):
            VASDefaultPassesEnabled(enabled_passes=[1, 7])

    def test_default_passes_enabled_empty_invalid(self) -> None:
        """Empty list should be invalid - at least one pass required."""
        from vtap100.models.vas import VASDefaultPassesEnabled

        with pytest.raises(ValidationError):
            VASDefaultPassesEnabled(enabled_passes=[])


class TestVASKeySlotOptional:
    """KeySlot per the manufacturer: '=0 or omitted (default)'."""

    def test_key_slot_may_be_omitted(self) -> None:
        """A VAS config without a key slot is valid; the reader auto-selects."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(merchant_id="pass.com.example.x")
        assert config.key_slot is None

    def test_key_slot_zero_is_valid(self) -> None:
        """Zero means automatic key selection."""
        from vtap100.models.vas import AppleVASConfig

        assert AppleVASConfig(merchant_id="pass.com.example.x", key_slot=0).key_slot == 0

    def test_key_slot_seven_is_rejected(self) -> None:
        """Above the documented range is an error."""
        from vtap100.models.vas import AppleVASConfig

        with pytest.raises(ValidationError):
            AppleVASConfig(merchant_id="pass.com.example.x", key_slot=7)

    def test_omitted_key_slot_emits_no_line(self) -> None:
        """An absent key slot must not appear in the output."""
        from vtap100.models.vas import AppleVASConfig

        lines = AppleVASConfig(merchant_id="pass.com.example.x").to_config_lines(1)
        assert lines == ["VAS1MerchantID=pass.com.example.x"]
