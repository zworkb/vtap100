"""Unit tests for Keyboard Emulation configuration model.

TDD Red Phase: These tests define the expected behavior of the KeyboardConfig model.
Tests should fail until the implementation is complete.

Phase 1 focuses on basic keyboard emulation: KBLogMode, KBSource, KBEnable
"""

from pydantic import ValidationError
import pytest


class TestKeyboardConfig:
    """Tests for KeyboardConfig model."""

    def test_keyboard_config_defaults(self) -> None:
        """Keyboard config should have sensible defaults."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.log_mode is False  # KBLogMode=0 by default
        assert config.enable is None  # absent unless the file sets it
        assert config.source == "A5"  # Default source

    def test_keyboard_config_log_mode_enabled(self) -> None:
        """Can enable keyboard log mode."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True)
        assert config.log_mode is True

    def test_keyboard_config_log_mode_disabled(self) -> None:
        """Can disable keyboard log mode."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=False)
        assert config.log_mode is False

    def test_keyboard_config_enable_flag(self) -> None:
        """Can set USB keyboard device enable flag."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(enable=False)
        assert config.enable is False

        config = KeyboardConfig(enable=True)
        assert config.enable is True

    def test_keyboard_config_source_valid_hex(self) -> None:
        """Source can be a valid hex string."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(source="A1")
        assert config.source == "A1"

        config = KeyboardConfig(source="FF")
        assert config.source == "FF"

    def test_keyboard_config_source_common_values(self) -> None:
        """Source accepts common hex bitmask values."""
        from vtap100.models.keyboard import KeyboardConfig

        # 80 = Mobile pass only (0x80)
        config = KeyboardConfig(source="80")
        assert config.source == "80"

        # A1 = Mobile pass + card emulation + card/tag UID (0x80+0x20+0x01)
        config = KeyboardConfig(source="A1")
        assert config.source == "A1"

        # A5 = Default: mobile pass + card emulation + scanners + UID
        config = KeyboardConfig(source="A5")
        assert config.source == "A5"


class TestKeyboardConfigOutput:
    """Tests for KeyboardConfig config.txt output generation."""

    def test_to_config_lines_default(self) -> None:
        """Default config should generate minimal output."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        lines = config.to_config_lines()

        # log_mode=False means KBLogMode=0, which is default - might not be in output
        # enable=True means KBEnable=1, which is default - might not be in output
        # source=A5 is default - might not be in output
        assert isinstance(lines, list)

    def test_to_config_lines_log_mode_enabled(self) -> None:
        """Enabled log mode should generate KBLogMode=1."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True)
        lines = config.to_config_lines()

        assert "KBLogMode=1" in lines

    def test_to_config_lines_log_mode_disabled(self) -> None:
        """Disabled log mode should generate KBLogMode=0."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=False)
        lines = config.to_config_lines()

        assert "KBLogMode=0" in lines

    def test_to_config_lines_enable_disabled(self) -> None:
        """Disabled keyboard should generate KBEnable=0."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(enable=False)
        lines = config.to_config_lines()

        assert "KBEnable=0" in lines

    def test_to_config_lines_source(self) -> None:
        """Custom source should be included."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(source="A1", log_mode=True)
        lines = config.to_config_lines()

        assert "KBSource=A1" in lines

    def test_to_config_lines_full_config(self) -> None:
        """Full config should generate all relevant lines."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(
            log_mode=True,
            enable=True,
            source="A1",
        )
        lines = config.to_config_lines()

        assert "KBLogMode=1" in lines
        assert "KBSource=A1" in lines
        # KBEnable=1 is default, might not be in output

    def test_to_config_lines_returns_list(self) -> None:
        """to_config_lines should return a list of strings."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        lines = config.to_config_lines()

        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)


class TestKBSourceBuilder:
    """Tests for KBSourceBuilder - builds hex bitmask values.

    KBSource uses hexadecimal bitmasks per official VTAP documentation:
    - Bit 7 (0x80): Mobile Pass (Apple VAS / Google Smart Tap)
    - Bit 6 (0x40): STUID
    - Bit 5 (0x20): Card Emulation Write Mode
    - Bit 2 (0x04): Scanners
    - Bit 1 (0x02): Command Interface
    - Bit 0 (0x01): Card/Tag UID

    Reference: https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm
    """

    def test_kb_source_mobile_pass_only(self) -> None:
        """Mobile pass only = 0x80 = '80'."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().mobile_pass().build()
        assert source == "80"

    def test_kb_source_card_tag_uid_only(self) -> None:
        """Card/Tag UID only = 0x01 = '01'."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().card_tag_uid().build()
        assert source == "01"

    def test_kb_source_card_emulation_only(self) -> None:
        """Card emulation write mode = 0x20 = '20'."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().card_emulation().build()
        assert source == "20"

    def test_kb_source_scanners_only(self) -> None:
        """Scanners = 0x04 = '04'."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().scanners().build()
        assert source == "04"

    def test_kb_source_command_interface_only(self) -> None:
        """Command interface = 0x02 = '02'."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().command_interface().build()
        assert source == "02"

    def test_kb_source_stuid_only(self) -> None:
        """STUID = 0x40 = '40'."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().stuid().build()
        assert source == "40"

    def test_kb_source_default_a5(self) -> None:
        """Default A5 = mobile_pass + card_emulation + scanners + card_tag_uid."""
        from vtap100.models.keyboard import KBSourceBuilder

        # A5 = 0x80 + 0x20 + 0x04 + 0x01 = 165 = 0xA5
        source = KBSourceBuilder().mobile_pass().card_emulation().scanners().card_tag_uid().build()
        assert source == "A5"

    def test_kb_source_common_a1(self) -> None:
        """Common A1 = mobile_pass + card_emulation + card_tag_uid."""
        from vtap100.models.keyboard import KBSourceBuilder

        # A1 = 0x80 + 0x20 + 0x01 = 161 = 0xA1
        source = KBSourceBuilder().mobile_pass().card_emulation().card_tag_uid().build()
        assert source == "A1"

    def test_kb_source_empty_returns_00(self) -> None:
        """Empty builder returns '00'."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().build()
        assert source == "00"

    def test_kb_source_no_duplicates(self) -> None:
        """Adding same bit twice doesn't change result (idempotent)."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().mobile_pass().mobile_pass().mobile_pass().build()
        assert source == "80"

    def test_kb_source_all_bits(self) -> None:
        """All bits set = 0xFF (assuming all defined bits)."""
        from vtap100.models.keyboard import KBSourceBuilder

        # 0x80 + 0x40 + 0x20 + 0x04 + 0x02 + 0x01 = 0xE7
        source = (
            KBSourceBuilder()
            .mobile_pass()
            .stuid()
            .card_emulation()
            .scanners()
            .command_interface()
            .card_tag_uid()
            .build()
        )
        assert source == "E7"

    def test_kb_source_fluent_api(self) -> None:
        """Builder supports fluent chaining."""
        from vtap100.models.keyboard import KBSourceBuilder

        builder = KBSourceBuilder()
        result = builder.mobile_pass().card_tag_uid()
        assert result is builder  # Returns self for chaining

    def test_kb_source_hex_uppercase(self) -> None:
        """Output should be uppercase hex."""
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().mobile_pass().card_tag_uid().build()
        assert source == "81"
        assert source == source.upper()


class TestKeyboardConfigExtended:
    """Tests for extended keyboard configuration (Phase 2)."""

    def test_keyboard_prefix_default(self) -> None:
        """Prefix should be None by default."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.prefix is None

    def test_keyboard_prefix_ascii_hex(self) -> None:
        """Can set prefix as ASCII hex string."""
        from vtap100.models.keyboard import KeyboardConfig

        # %0A is newline in ASCII hex
        config = KeyboardConfig(prefix="%0A")
        assert config.prefix == "%0A"

    def test_keyboard_prefix_variable(self) -> None:
        """Can set prefix with variable like $t (timestamp)."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(prefix="$t")
        assert config.prefix == "$t"

    def test_keyboard_postfix_default(self) -> None:
        """Postfix is absent unless the file sets it.

        The reader's own default is %0A. Keeping the model value None is what
        lets an explicit KBPostfix=%0A survive a round-trip.
        """
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.postfix is None

    def test_keyboard_postfix_custom(self) -> None:
        """Can set custom postfix."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(postfix="%0D%0A")  # CRLF
        assert config.postfix == "%0D%0A"

    def test_keyboard_delay_default(self) -> None:
        """Delay is absent unless the file sets it (reader default 5ms)."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.delay_ms is None

    def test_keyboard_delay_valid_range(self) -> None:
        """Delay is accepted across the technically valid range."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(delay_ms=5)
        assert config.delay_ms == 5

        config = KeyboardConfig(delay_ms=255)
        assert config.delay_ms == 255

        config = KeyboardConfig(delay_ms=100)
        assert config.delay_ms == 100

    def test_keyboard_delay_below_documented_min_is_accepted(self) -> None:
        """Delay below 5 parses.

        The manufacturer documents 5-255 but ships a sample config.txt using
        KBDelayMS=2. Parsing is tolerant so that file loads; the strict bound
        belongs on the TUI input, not on the model.
        """
        from vtap100.models.keyboard import KeyboardConfig

        assert KeyboardConfig(delay_ms=2).delay_ms == 2

    def test_keyboard_delay_above_max_fails(self) -> None:
        """Delay above 255 should fail validation."""
        from vtap100.models.keyboard import KeyboardConfig

        with pytest.raises(ValidationError):
            KeyboardConfig(delay_ms=256)

    def test_keyboard_pass_mode_default(self) -> None:
        """Pass mode is absent unless the file sets it (reader default off)."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.pass_mode is None

    def test_keyboard_pass_mode_enabled(self) -> None:
        """Can enable pass mode for payload extraction."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(pass_mode=True)
        assert config.pass_mode is True

    def test_keyboard_pass_section_default(self) -> None:
        """Pass section is absent unless the file sets it (reader default 0)."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.pass_section is None

    def test_keyboard_pass_section_custom(self) -> None:
        """Can set custom pass section."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(pass_section=2)
        assert config.pass_section == 2

    def test_keyboard_pass_separator_default(self) -> None:
        """Pass separator should default to pipe character."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.pass_separator is None

    def test_keyboard_pass_separator_custom(self) -> None:
        """Can set custom pass separator."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(pass_separator=";")
        assert config.pass_separator == ";"

    def test_keyboard_pass_start_default(self) -> None:
        """Pass start position should default to 0."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.pass_start is None

    def test_keyboard_pass_start_custom(self) -> None:
        """Can set custom pass start position."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(pass_start=10)
        assert config.pass_start == 10

    def test_keyboard_pass_length_default(self) -> None:
        """Pass length should default to 0 (all data)."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig()
        assert config.pass_length is None

    def test_keyboard_pass_length_custom(self) -> None:
        """Can set custom pass length."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(pass_length=16)
        assert config.pass_length == 16


class TestKeyboardConfigExtendedOutput:
    """Tests for extended keyboard config.txt output generation."""

    def test_to_config_lines_with_prefix(self) -> None:
        """Prefix should generate KBPrefix line."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, prefix="$t")
        lines = config.to_config_lines()

        assert "KBPrefix=$t" in lines

    def test_to_config_lines_with_postfix(self) -> None:
        """Non-default postfix should generate KBPostfix line."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, postfix="%0D%0A")
        lines = config.to_config_lines()

        assert "KBPostfix=%0D%0A" in lines

    def test_to_config_lines_default_postfix_not_included(self) -> None:
        """Default postfix (%0A) should not be in output."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True)
        lines = config.to_config_lines()

        # Default %0A should not be explicitly in output
        assert not any("KBPostfix=%0A" in line for line in lines)

    def test_to_config_lines_with_delay(self) -> None:
        """Non-default delay should generate KBDelayMS line."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, delay_ms=50)
        lines = config.to_config_lines()

        assert "KBDelayMS=50" in lines

    def test_to_config_lines_explicit_delay_is_included(self) -> None:
        """An explicitly set delay is emitted even when it equals the default."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, delay_ms=5)
        lines = config.to_config_lines()

        assert "KBDelayMS=5" in lines

    def test_to_config_lines_with_pass_mode(self) -> None:
        """Enabled pass mode should generate KBPassMode=1."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, pass_mode=True)
        lines = config.to_config_lines()

        assert "KBPassMode=1" in lines

    def test_to_config_lines_pass_section(self) -> None:
        """Non-zero pass section should generate KBPassSection line."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, pass_mode=True, pass_section=2)
        lines = config.to_config_lines()

        assert "KBPassSection=2" in lines

    def test_to_config_lines_pass_separator(self) -> None:
        """Non-default pass separator should generate KBPassSeparator line."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, pass_mode=True, pass_separator=";")
        lines = config.to_config_lines()

        assert "KBPassSeparator=;" in lines

    def test_to_config_lines_pass_start(self) -> None:
        """Non-zero pass start should generate KBPassStart line."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, pass_mode=True, pass_start=5)
        lines = config.to_config_lines()

        assert "KBPassStart=5" in lines

    def test_to_config_lines_pass_length(self) -> None:
        """Non-zero pass length should generate KBPassLength line."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(log_mode=True, pass_mode=True, pass_length=16)
        lines = config.to_config_lines()

        assert "KBPassLength=16" in lines

    def test_to_config_lines_full_extended_config(self) -> None:
        """Full extended config should generate all relevant lines."""
        from vtap100.models.keyboard import KeyboardConfig

        config = KeyboardConfig(
            log_mode=True,
            source="A1",  # Valid hex: mobile pass + card emulation + UID
            prefix="$t:",
            postfix="%0D%0A",
            delay_ms=50,
            pass_mode=True,
            pass_section=1,
            pass_separator=";",
            pass_start=0,
            pass_length=32,
        )
        lines = config.to_config_lines()

        assert "KBLogMode=1" in lines
        assert "KBSource=A1" in lines
        assert "KBPrefix=$t:" in lines
        assert "KBPostfix=%0D%0A" in lines
        assert "KBDelayMS=50" in lines
        assert "KBPassMode=1" in lines
        assert "KBPassSection=1" in lines
        assert "KBPassSeparator=;" in lines
        assert "KBPassLength=32" in lines


class TestKBSourceParsing:
    """Tests for parsing KBSource hex strings to bit flags."""

    def test_parse_kbsource_hex_default_a5(self) -> None:
        """Default A5 should parse to mobile_pass + card_emulation + scanners + card_tag_uid."""
        from vtap100.models.keyboard import parse_kbsource_hex

        flags = parse_kbsource_hex("A5")
        assert flags["mobile_pass"] is True
        assert flags["stuid"] is False
        assert flags["card_emulation"] is True
        assert flags["scanners"] is True
        assert flags["command_interface"] is False
        assert flags["card_tag_uid"] is True

    def test_parse_kbsource_hex_mobile_only(self) -> None:
        """80 should parse to mobile_pass only."""
        from vtap100.models.keyboard import parse_kbsource_hex

        flags = parse_kbsource_hex("80")
        assert flags["mobile_pass"] is True
        assert flags["stuid"] is False
        assert flags["card_emulation"] is False
        assert flags["scanners"] is False
        assert flags["command_interface"] is False
        assert flags["card_tag_uid"] is False

    def test_parse_kbsource_hex_all_bits(self) -> None:
        """E7 should parse to all defined bits set."""
        from vtap100.models.keyboard import parse_kbsource_hex

        flags = parse_kbsource_hex("E7")
        assert flags["mobile_pass"] is True
        assert flags["stuid"] is True
        assert flags["card_emulation"] is True
        assert flags["scanners"] is True
        assert flags["command_interface"] is True
        assert flags["card_tag_uid"] is True

    def test_parse_kbsource_hex_zero(self) -> None:
        """00 should parse to all bits off."""
        from vtap100.models.keyboard import parse_kbsource_hex

        flags = parse_kbsource_hex("00")
        assert all(not v for v in flags.values())

    def test_parse_kbsource_hex_lowercase(self) -> None:
        """Should handle lowercase hex input."""
        from vtap100.models.keyboard import parse_kbsource_hex

        flags = parse_kbsource_hex("a5")
        assert flags["mobile_pass"] is True
        assert flags["card_tag_uid"] is True

    def test_parse_kbsource_hex_invalid(self) -> None:
        """Invalid hex should raise ValueError."""
        from vtap100.models.keyboard import parse_kbsource_hex

        with pytest.raises(ValueError):
            parse_kbsource_hex("GG")


class TestKBSourceBuilding:
    """Tests for building KBSource hex from flags."""

    def test_build_kbsource_from_flags_default(self) -> None:
        """A5 configuration from individual flags."""
        from vtap100.models.keyboard import build_kbsource_from_flags

        result = build_kbsource_from_flags(
            mobile_pass=True,
            card_emulation=True,
            scanners=True,
            card_tag_uid=True,
        )
        assert result == "A5"

    def test_build_kbsource_from_flags_empty(self) -> None:
        """No flags should return 00."""
        from vtap100.models.keyboard import build_kbsource_from_flags

        result = build_kbsource_from_flags()
        assert result == "00"

    def test_build_kbsource_from_flags_all(self) -> None:
        """All flags should return E7."""
        from vtap100.models.keyboard import build_kbsource_from_flags

        result = build_kbsource_from_flags(
            mobile_pass=True,
            stuid=True,
            card_emulation=True,
            scanners=True,
            command_interface=True,
            card_tag_uid=True,
        )
        assert result == "E7"

    def test_build_kbsource_from_flags_single_bits(self) -> None:
        """Each single bit should produce correct hex."""
        from vtap100.models.keyboard import build_kbsource_from_flags

        assert build_kbsource_from_flags(mobile_pass=True) == "80"
        assert build_kbsource_from_flags(stuid=True) == "40"
        assert build_kbsource_from_flags(card_emulation=True) == "20"
        assert build_kbsource_from_flags(scanners=True) == "04"
        assert build_kbsource_from_flags(command_interface=True) == "02"
        assert build_kbsource_from_flags(card_tag_uid=True) == "01"

    def test_build_kbsource_roundtrip(self) -> None:
        """Parse and rebuild should give same result."""
        from vtap100.models.keyboard import build_kbsource_from_flags
        from vtap100.models.keyboard import parse_kbsource_hex

        original = "A5"
        flags = parse_kbsource_hex(original)
        rebuilt = build_kbsource_from_flags(**flags)
        assert rebuilt == original

    def test_build_kbsource_roundtrip_all_values(self) -> None:
        """Roundtrip should work for various hex values."""
        from vtap100.models.keyboard import build_kbsource_from_flags
        from vtap100.models.keyboard import parse_kbsource_hex

        for hex_val in ["00", "01", "80", "A1", "A5", "E7"]:
            flags = parse_kbsource_hex(hex_val)
            rebuilt = build_kbsource_from_flags(**flags)
            assert rebuilt == hex_val, f"Roundtrip failed for {hex_val}"
