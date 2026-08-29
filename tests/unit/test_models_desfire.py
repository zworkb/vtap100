"""Unit tests for MIFARE DESFire configuration model.

TDD Red Phase: These tests define the expected behavior of the DESFireConfig model.
Tests should fail until the implementation is complete.

Phase 4 focuses on MIFARE DESFire settings.
"""

from pydantic import ValidationError
import pytest


class TestDESFireCryptoMode:
    """Tests for DESFireCryptoMode enum."""

    def test_crypto_none(self) -> None:
        """Mode 0 means no encryption."""
        from vtap100.models.desfire import DESFireCryptoMode

        assert DESFireCryptoMode.NONE.value == 0

    def test_crypto_3des(self) -> None:
        """Mode 1 means 3DES encryption."""
        from vtap100.models.desfire import DESFireCryptoMode

        assert DESFireCryptoMode.DES3.value == 1

    def test_crypto_aes(self) -> None:
        """Mode 3 means AES encryption."""
        from vtap100.models.desfire import DESFireCryptoMode

        assert DESFireCryptoMode.AES.value == 3


class TestDESFireDataFormat:
    """Tests for DESFireDataFormat enum."""

    def test_format_raw(self) -> None:
        """Format 0 means raw data."""
        from vtap100.models.desfire import DESFireDataFormat

        assert DESFireDataFormat.RAW.value == 0

    def test_format_keyid_v1(self) -> None:
        """Format 1 means KEY-ID v1."""
        from vtap100.models.desfire import DESFireDataFormat

        assert DESFireDataFormat.KEYID_V1.value == 1

    def test_format_keyid_v2(self) -> None:
        """Format 2 means KEY-ID v2."""
        from vtap100.models.desfire import DESFireDataFormat

        assert DESFireDataFormat.KEYID_V2.value == 2


class TestDESFireAppConfig:
    """Tests for single DESFire application configuration."""

    def test_desfire_app_defaults(self) -> None:
        """DESFire app config should have sensible defaults."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC")
        assert config.app_id == "AABBCC"
        assert config.file_id is None
        assert config.key_num is None
        assert config.key_slot is None
        assert config.crypto is None
        assert config.format is None
        # Absent, not defaulted: the reader's own defaults are 3 and 0, but
        # keeping the model value None is what lets an explicit
        # DESFire1ReadOffset=0 survive a round-trip.
        assert config.read_length is None
        assert config.read_offset is None

    def test_desfire_app_id_required(self) -> None:
        """App ID is required."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig()

    def test_desfire_app_id_hex_format(self) -> None:
        """App ID must be 6 hex characters."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC")
        assert config.app_id == "AABBCC"

        config = DESFireAppConfig(app_id="123456")
        assert config.app_id == "123456"

    def test_desfire_file_id_range(self) -> None:
        """File ID must be 1-255."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", file_id=1)
        assert config.file_id == 1

        config = DESFireAppConfig(app_id="AABBCC", file_id=255)
        assert config.file_id == 255

    def test_desfire_file_id_negative_invalid(self) -> None:
        """File ID below 0 should fail.

        File 0 itself is valid: the manufacturer documents "Use a value from 0
        to 255", and real deployment configs read from file 0.
        """
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", file_id=-1)

    def test_desfire_file_id_above_max_invalid(self) -> None:
        """File ID above 255 should fail."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", file_id=256)

    def test_desfire_key_slot_range(self) -> None:
        """Key slot must be 1-9."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", key_slot=1)
        assert config.key_slot == 1

        config = DESFireAppConfig(app_id="AABBCC", key_slot=9)
        assert config.key_slot == 9

    def test_desfire_key_slot_zero_invalid(self) -> None:
        """Key slot 0 should fail."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", key_slot=0)

    def test_desfire_key_slot_above_max_invalid(self) -> None:
        """Key slot above 9 should fail."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", key_slot=10)

    def test_desfire_crypto_mode(self) -> None:
        """Can set crypto mode."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireCryptoMode

        config = DESFireAppConfig(app_id="AABBCC", crypto=DESFireCryptoMode.AES)
        assert config.crypto == DESFireCryptoMode.AES

    def test_desfire_format(self) -> None:
        """Can set data format."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireDataFormat

        config = DESFireAppConfig(app_id="AABBCC", format=DESFireDataFormat.KEYID_V1)
        assert config.format == DESFireDataFormat.KEYID_V1

    def test_desfire_read_length_range(self) -> None:
        """Read length must be 1-255."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", read_length=1)
        assert config.read_length == 1

        config = DESFireAppConfig(app_id="AABBCC", read_length=255)
        assert config.read_length == 255

    def test_desfire_read_length_zero_invalid(self) -> None:
        """Read length 0 should fail."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", read_length=0)

    def test_desfire_read_offset_range(self) -> None:
        """Read offset must be 0-255."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", read_offset=0)
        assert config.read_offset == 0

        config = DESFireAppConfig(app_id="AABBCC", read_offset=255)
        assert config.read_offset == 255

    def test_desfire_read_offset_above_max_invalid(self) -> None:
        """Read offset above 255 should fail."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", read_offset=256)

    def test_desfire_diversification(self) -> None:
        """Can enable key diversification.

        Mode 1 is AN10922 over UID and AID, the standard setting.
        """
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", diversification=1)
        assert config.diversification == 1

    def test_desfire_privacy_key(self) -> None:
        """Can set privacy key settings."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(
            app_id="AABBCC",
            privacy_key_num=1,
            privacy_key_slot=2,
        )
        assert config.privacy_key_num == 1
        assert config.privacy_key_slot == 2

    def test_desfire_sysid(self) -> None:
        """Can set system ID settings."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(
            app_id="AABBCC",
            sysid_key_slot=3,
            sysid_length=8,
        )
        assert config.sysid_key_slot == 3
        assert config.sysid_length == 8

    def test_desfire_sysid_length_range(self) -> None:
        """System ID length must be 0-16."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", sysid_length=0)
        assert config.sysid_length == 0

        config = DESFireAppConfig(app_id="AABBCC", sysid_length=16)
        assert config.sysid_length == 16

    def test_desfire_sysid_length_above_max_invalid(self) -> None:
        """System ID length above 16 should fail."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", sysid_length=17)


class TestDESFireConfig:
    """Tests for DESFireConfig model (multiple apps)."""

    def test_desfire_config_defaults(self) -> None:
        """DESFire config should have sensible defaults."""
        from vtap100.models.desfire import DESFireConfig

        config = DESFireConfig()
        assert config.apps == []
        assert config.separator == ","

    def test_desfire_config_single_app(self) -> None:
        """Can configure single DESFire app."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig

        app = DESFireAppConfig(app_id="AABBCC", file_id=1)
        config = DESFireConfig(apps=[app])

        assert len(config.apps) == 1
        assert config.apps[0].app_id == "AABBCC"

    def test_desfire_config_multiple_apps(self) -> None:
        """Can configure up to 9 DESFire apps."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig

        apps = [DESFireAppConfig(app_id=f"00000{i}") for i in range(1, 10)]
        config = DESFireConfig(apps=apps)

        assert len(config.apps) == 9

    def test_desfire_config_max_apps(self) -> None:
        """Cannot have more than 9 apps."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig

        apps = [DESFireAppConfig(app_id=f"0000{i:02d}") for i in range(10)]

        with pytest.raises(ValidationError):
            DESFireConfig(apps=apps)

    def test_desfire_config_separator(self) -> None:
        """Can set custom separator."""
        from vtap100.models.desfire import DESFireConfig

        config = DESFireConfig(separator=";")
        assert config.separator == ";"


class TestDESFireAppConfigOutput:
    """Tests for DESFireAppConfig config.txt output generation."""

    def test_to_config_lines_minimal(self) -> None:
        """Minimal config should generate AppID line."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC")
        lines = config.to_config_lines(slot_number=1)

        assert "DESFire1AppID=AABBCC" in lines

    def test_to_config_lines_with_file_id(self) -> None:
        """File ID should generate DESFire#FileID line."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", file_id=5)
        lines = config.to_config_lines(slot_number=1)

        assert "DESFire1FileID=5" in lines

    def test_to_config_lines_with_key(self) -> None:
        """Key settings should generate lines."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", key_num=0, key_slot=2)
        lines = config.to_config_lines(slot_number=1)

        assert "DESFire1KeyNum=0" in lines
        assert "DESFire1KeySlot=2" in lines

    def test_to_config_lines_with_crypto(self) -> None:
        """Crypto mode should generate DESFire#Crypto line."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireCryptoMode

        config = DESFireAppConfig(app_id="AABBCC", crypto=DESFireCryptoMode.AES)
        lines = config.to_config_lines(slot_number=1)

        assert "DESFire1Crypto=3" in lines

    def test_to_config_lines_with_format(self) -> None:
        """Format should generate DESFire#Format line."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireDataFormat

        config = DESFireAppConfig(app_id="AABBCC", format=DESFireDataFormat.KEYID_V2)
        lines = config.to_config_lines(slot_number=1)

        assert "DESFire1Format=2" in lines

    def test_to_config_lines_with_read_settings(self) -> None:
        """Read settings should generate lines."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", read_length=16, read_offset=4)
        lines = config.to_config_lines(slot_number=1)

        assert "DESFire1ReadLength=16" in lines
        assert "DESFire1ReadOffset=4" in lines

    def test_to_config_lines_default_read_length_not_included(self) -> None:
        """Default read length (3) should not be in output."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC")
        lines = config.to_config_lines(slot_number=1)

        assert not any("ReadLength" in line for line in lines)

    def test_to_config_lines_with_diversification(self) -> None:
        """Diversification should generate DESFire#Diversification=1."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", diversification=True)
        lines = config.to_config_lines(slot_number=1)

        assert "DESFire1Diversification=1" in lines

    def test_to_config_lines_slot_number(self) -> None:
        """Different slot numbers should generate different prefixes."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC")

        lines1 = config.to_config_lines(slot_number=1)
        assert "DESFire1AppID=AABBCC" in lines1

        lines5 = config.to_config_lines(slot_number=5)
        assert "DESFire5AppID=AABBCC" in lines5

    def test_to_config_lines_full_config(self) -> None:
        """Full config should generate all lines."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireCryptoMode
        from vtap100.models.desfire import DESFireDataFormat

        config = DESFireAppConfig(
            app_id="AABBCC",
            file_id=1,
            key_num=0,
            key_slot=2,
            crypto=DESFireCryptoMode.AES,
            format=DESFireDataFormat.RAW,
            read_length=16,
            read_offset=0,
            diversification=True,
        )
        lines = config.to_config_lines(slot_number=1)

        assert "DESFire1AppID=AABBCC" in lines
        assert "DESFire1FileID=1" in lines
        assert "DESFire1KeyNum=0" in lines
        assert "DESFire1KeySlot=2" in lines
        assert "DESFire1Crypto=3" in lines
        assert "DESFire1Format=0" in lines
        assert "DESFire1ReadLength=16" in lines
        assert "DESFire1Diversification=1" in lines


class TestDESFireConfigOutput:
    """Tests for DESFireConfig config.txt output generation."""

    def test_to_config_lines_empty(self) -> None:
        """Empty config should generate no lines."""
        from vtap100.models.desfire import DESFireConfig

        config = DESFireConfig()
        lines = config.to_config_lines()

        assert lines == []

    def test_to_config_lines_single_app(self) -> None:
        """Single app should generate numbered lines."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig

        app = DESFireAppConfig(app_id="AABBCC")
        config = DESFireConfig(apps=[app])
        lines = config.to_config_lines()

        assert "DESFire1AppID=AABBCC" in lines

    def test_to_config_lines_multiple_apps(self) -> None:
        """Multiple apps should generate correctly numbered lines."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig

        apps = [
            DESFireAppConfig(app_id="111111"),
            DESFireAppConfig(app_id="222222"),
            DESFireAppConfig(app_id="333333"),
        ]
        config = DESFireConfig(apps=apps)
        lines = config.to_config_lines()

        assert "DESFire1AppID=111111" in lines
        assert "DESFire2AppID=222222" in lines
        assert "DESFire3AppID=333333" in lines

    def test_to_config_lines_with_separator(self) -> None:
        """Non-default separator should generate DESFireSeparator line."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig

        app = DESFireAppConfig(app_id="AABBCC")
        config = DESFireConfig(apps=[app], separator=";")
        lines = config.to_config_lines()

        assert "DESFireSeparator=;" in lines

    def test_to_config_lines_default_separator_not_included(self) -> None:
        """Default separator (,) should not be in output."""
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig

        app = DESFireAppConfig(app_id="AABBCC")
        config = DESFireConfig(apps=[app])
        lines = config.to_config_lines()

        assert not any("DESFireSeparator" in line for line in lines)


class TestDESFireFileIdRange:
    """FileID range per the manufacturer: 'Use a value from 0 to 255'."""

    def test_file_id_zero_is_valid(self) -> None:
        """File 0 is a legal DESFire file number and appears in real configs."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", file_id=0)
        assert config.file_id == 0

    def test_file_id_255_is_valid(self) -> None:
        """Upper bound is inclusive."""
        from vtap100.models.desfire import DESFireAppConfig

        assert DESFireAppConfig(app_id="AABBCC", file_id=255).file_id == 255

    def test_file_id_256_is_rejected(self) -> None:
        """Above the documented range is still an error."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", file_id=256)


class TestDiversificationBitField:
    """Diversification is a bit field, not a switch.

    Bit 0 enables AN10922, bit 1 omits the AID from the input, bit 2 reverses
    UID byte order. Valid values are therefore 0, 1, 3, 5 and 7.
    """

    @pytest.mark.parametrize("value", [0, 1, 3, 5, 7])
    def test_documented_values_are_accepted(self, value: int) -> None:
        """Every documented mode is valid."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", diversification=value)
        assert config.diversification == value

    @pytest.mark.parametrize("value", [2, 4, 6])
    def test_modifier_without_active_bit_is_rejected(self, value: int) -> None:
        """A modifier bit without bit 0 means nothing."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", diversification=value)

    def test_out_of_range_is_rejected(self) -> None:
        """Only three bits exist."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", diversification=8)

    def test_builder_composes_bits(self) -> None:
        """The builder mirrors KBSourceBuilder for the other bitmask setting."""
        from vtap100.models.desfire import DiversificationBuilder

        assert DiversificationBuilder().active().build() == 1
        assert DiversificationBuilder().active().omit_aid().build() == 3
        assert DiversificationBuilder().active().reverse_uid().build() == 5
        assert DiversificationBuilder().active().omit_aid().reverse_uid().build() == 7


class TestDESFireRemainingRanges:
    """Ranges the model left unchecked."""

    @pytest.mark.parametrize(
        ("field_name", "valid", "invalid"),
        [
            ("key_num", 15, 16),
            ("sysid_key_slot", 9, 10),
            ("privacy_key_slot", 9, 10),
        ],
    )
    def test_upper_bound(self, field_name: str, valid: int, invalid: int) -> None:
        """The documented upper bound is enforced."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", **{field_name: valid})
        assert getattr(config, field_name) == valid
        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", **{field_name: invalid})

    def test_privacy_key_slot_zero_is_rejected(self) -> None:
        """Privacy key slots are 1-9; there is no 'none' value."""
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", privacy_key_slot=0)

    def test_sysid_key_slot_zero_is_valid(self) -> None:
        """SysIDKeySlot=0 means 'do not use a System Identifier'."""
        from vtap100.models.desfire import DESFireAppConfig

        assert DESFireAppConfig(app_id="AABBCC", sysid_key_slot=0).sysid_key_slot == 0


class TestDESFireReadDefaults:
    """An explicitly set default value must keep its line."""

    def test_explicit_read_offset_zero_is_preserved(self) -> None:
        """ReadOffset=0 is also the default, and must not vanish."""
        from vtap100.roundtrip import compare

        report = compare("!VTAPconfig\nDESFire1AppID=AABBCC\nDESFire1ReadOffset=0\n")
        assert report.lost == []

    def test_explicit_read_length_three_is_preserved(self) -> None:
        """ReadLength=3 is also the default."""
        from vtap100.roundtrip import compare

        report = compare("!VTAPconfig\nDESFire1AppID=AABBCC\nDESFire1ReadLength=3\n")
        assert report.lost == []
