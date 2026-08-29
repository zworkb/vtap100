"""Unit tests for config.txt parser.

TDD: Tests for parsing config.txt back into VTAPConfig.
"""

import pytest


class TestConfigParserImports:
    """Test that parser module can be imported."""

    def test_import_config_parser(self) -> None:
        """ConfigParser should be importable."""
        from vtap100.parser import ConfigParser

        assert ConfigParser is not None

    def test_import_parse_function(self) -> None:
        """Parse function should be importable."""
        from vtap100.parser import parse

        assert callable(parse)


class TestConfigParserHeader:
    """Test header validation."""

    def test_parse_valid_header(self) -> None:
        """Valid config should start with !VTAPconfig."""
        from vtap100.parser import parse

        content = "!VTAPconfig\n"
        config = parse(content)
        assert config is not None

    def test_parse_missing_header_raises(self) -> None:
        """Missing header should raise ValueError."""
        from vtap100.parser import parse

        content = "VAS1MerchantID=pass.com.test\n"
        with pytest.raises(ValueError, match="header"):
            parse(content)

    def test_parse_empty_config(self) -> None:
        """Empty config (just header) should be valid."""
        from vtap100.parser import parse

        content = "!VTAPconfig"
        config = parse(content)
        assert config.vas_configs == []
        assert config.smarttap_configs == []


class TestConfigParserVAS:
    """Test VAS configuration parsing."""

    def test_parse_single_vas(self) -> None:
        """Parse single VAS config."""
        from vtap100.parser import parse

        content = """!VTAPconfig
VAS1MerchantID=pass.com.example.test
VAS1KeySlot=1
"""
        config = parse(content)
        assert len(config.vas_configs) == 1
        assert config.vas_configs[0].merchant_id == "pass.com.example.test"
        assert config.vas_configs[0].key_slot == 1

    def test_parse_vas_with_url(self) -> None:
        """Parse VAS config with optional merchant URL."""
        from vtap100.parser import parse

        content = """!VTAPconfig
VAS1MerchantID=pass.com.example.test
VAS1KeySlot=1
VAS1MerchantURL=https://example.com
"""
        config = parse(content)
        assert config.vas_configs[0].merchant_url == "https://example.com"

    def test_parse_multiple_vas(self) -> None:
        """Parse multiple VAS configs."""
        from vtap100.parser import parse

        content = """!VTAPconfig
VAS1MerchantID=pass.com.example.one
VAS1KeySlot=1
VAS2MerchantID=pass.com.example.two
VAS2KeySlot=2
"""
        config = parse(content)
        assert len(config.vas_configs) == 2
        assert config.vas_configs[0].merchant_id == "pass.com.example.one"
        assert config.vas_configs[1].merchant_id == "pass.com.example.two"


class TestConfigParserSmartTap:
    """Test Smart Tap configuration parsing."""

    def test_parse_single_smarttap(self) -> None:
        """Parse single Smart Tap config."""
        from vtap100.parser import parse

        content = """!VTAPconfig
ST1CollectorID=96972794
ST1KeySlot=2
ST1KeyVersion=1
"""
        config = parse(content)
        assert len(config.smarttap_configs) == 1
        assert config.smarttap_configs[0].collector_id == "96972794"
        assert config.smarttap_configs[0].key_slot == 2
        assert config.smarttap_configs[0].key_version == 1

    def test_parse_multiple_smarttap(self) -> None:
        """Parse multiple Smart Tap configs."""
        from vtap100.parser import parse

        content = """!VTAPconfig
ST1CollectorID=12345678
ST1KeySlot=1
ST2CollectorID=87654321
ST2KeySlot=2
"""
        config = parse(content)
        assert len(config.smarttap_configs) == 2


class TestConfigParserKeyboard:
    """Test keyboard configuration parsing."""

    def test_parse_keyboard_basic(self) -> None:
        """Parse basic keyboard config."""
        from vtap100.parser import parse

        content = """!VTAPconfig
KBLogMode=1
KBSource=A1
"""
        config = parse(content)
        assert config.keyboard is not None
        assert config.keyboard.log_mode is True
        assert config.keyboard.source == "A1"

    def test_parse_keyboard_log_mode_zero(self) -> None:
        """Parse keyboard with log_mode=0."""
        from vtap100.parser import parse

        content = """!VTAPconfig
KBLogMode=0
KBSource=AG
"""
        config = parse(content)
        assert config.keyboard.log_mode is False


class TestConfigParserComments:
    """Test comment handling."""

    def test_parse_ignores_comments(self) -> None:
        """Comments should be ignored."""
        from vtap100.parser import parse

        content = """!VTAPconfig
; This is a comment
VAS1MerchantID=pass.com.test
; Another comment
VAS1KeySlot=1
"""
        config = parse(content)
        assert len(config.vas_configs) == 1

    def test_parse_ignores_section_comments(self) -> None:
        """Section comments should be ignored."""
        from vtap100.parser import parse

        content = """!VTAPconfig
; Apple VAS Configuration
VAS1MerchantID=pass.com.test
VAS1KeySlot=1
; Google Smart Tap Configuration
ST1CollectorID=12345678
ST1KeySlot=2
"""
        config = parse(content)
        assert len(config.vas_configs) == 1
        assert len(config.smarttap_configs) == 1


class TestConfigParserCombined:
    """Test combined configuration parsing."""

    def test_parse_combined_config(self) -> None:
        """Parse config with VAS, Smart Tap, and Keyboard."""
        from vtap100.parser import parse

        content = """!VTAPconfig
; Apple VAS Configuration
VAS1MerchantID=pass.com.example.test
VAS1KeySlot=1
; Google Smart Tap Configuration
ST1CollectorID=96972794
ST1KeySlot=2
ST1KeyVersion=1
; Keyboard Emulation
KBLogMode=1
KBSource=AG
"""
        config = parse(content)
        assert len(config.vas_configs) == 1
        assert len(config.smarttap_configs) == 1
        assert config.keyboard is not None


class TestConfigParserIncompleteData:
    """Test parsing incomplete configuration data."""

    def test_parse_vas_without_merchant_id(self) -> None:
        """VAS config with only key_slot should not create config."""
        from vtap100.parser import parse

        content = """!VTAPconfig
VAS1KeySlot=1
"""
        config = parse(content)
        # Should not create VAS config since merchant_id is required
        assert len(config.vas_configs) == 0

    def test_parse_smarttap_without_collector_id(self) -> None:
        """Smart Tap config with only key_slot should not create config."""
        from vtap100.parser import parse

        content = """!VTAPconfig
ST1KeySlot=2
ST1KeyVersion=1
"""
        config = parse(content)
        # Should not create SmartTap config since collector_id is required
        assert len(config.smarttap_configs) == 0

    def test_parse_vas_partial_then_complete(self) -> None:
        """VAS config partial data followed by complete config."""
        from vtap100.parser import parse

        content = """!VTAPconfig
VAS1KeySlot=1
VAS2MerchantID=pass.com.example.test
VAS2KeySlot=2
"""
        config = parse(content)
        # Only VAS2 should be created since VAS1 has no merchant_id
        assert len(config.vas_configs) == 1
        assert config.vas_configs[0].merchant_id == "pass.com.example.test"
        assert config.vas_configs[0].key_slot == 2


class TestConfigParserRoundTrip:
    """Test generate -> parse roundtrip."""

    def test_roundtrip_vas(self) -> None:
        """Generate and parse VAS config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig
        from vtap100.parser import parse

        original = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)]
        )
        generator = ConfigGenerator(original)
        content = generator.generate()
        parsed = parse(content)

        assert len(parsed.vas_configs) == 1
        assert parsed.vas_configs[0].merchant_id == original.vas_configs[0].merchant_id
        assert parsed.vas_configs[0].key_slot == original.vas_configs[0].key_slot

    def test_roundtrip_combined(self) -> None:
        """Generate and parse combined config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.keyboard import KeyboardConfig
        from vtap100.models.smarttap import GoogleSmartTapConfig
        from vtap100.models.vas import AppleVASConfig
        from vtap100.parser import parse

        original = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)],
            smarttap_configs=[
                GoogleSmartTapConfig(slot=2, collector_id="96972794", key_slot=2, key_version=1)
            ],
            keyboard=KeyboardConfig(log_mode=True, source="AG"),
        )
        generator = ConfigGenerator(original)
        content = generator.generate()
        parsed = parse(content)

        assert len(parsed.vas_configs) == 1
        assert len(parsed.smarttap_configs) == 1
        assert parsed.keyboard is not None
        assert parsed.keyboard.log_mode is True


class TestConfigParserNFC:
    """Test NFC tag configuration parsing."""

    def test_parse_nfc_type2_uid(self) -> None:
        """Parse NFC Type 2 in UID mode."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType2=U
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.type2 is not None
        assert config.nfc.type2.value == "U"

    def test_parse_nfc_type4_ndef(self) -> None:
        """Parse NFC Type 4 in NDEF mode."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType4=N
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.type4 is not None
        assert config.nfc.type4.value == "N"

    def test_parse_nfc_type5_block(self) -> None:
        """Parse NFC Type 5 in BLOCK mode."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType5=B
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.type5 is not None
        assert config.nfc.type5.value == "B"

    def test_parse_nfc_type4_desfire(self) -> None:
        """Parse NFC Type 4 in DESFire mode."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType4=D
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.type4 is not None
        assert config.nfc.type4.value == "D"

    def test_parse_nfc_disabled(self) -> None:
        """Parse NFC Type disabled."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType2=0
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.type2 is not None
        assert config.nfc.type2.value == "0"

    def test_parse_nfc_all_types(self) -> None:
        """Parse all NFC types."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType2=U
NFCType4=N
NFCType5=B
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.type2.value == "U"
        assert config.nfc.type4.value == "N"
        assert config.nfc.type5.value == "B"

    def test_parse_nfc_report_read_error(self) -> None:
        """Parse NFCReportReadError setting."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType2=U
NFCReportReadError=1
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.report_read_error is True

    def test_parse_nfc_ignore_random_uid(self) -> None:
        """Parse IgnoreRandomUID setting."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType4=U
IgnoreRandomUID=1
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.ignore_random_uid is True

    def test_parse_nfc_byte_order(self) -> None:
        """Parse TagByteOrder setting."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType2=U
TagByteOrder=1
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.byte_order_reversed is True

    def test_parse_nfc_tag_read_config(self) -> None:
        """Parse TagRead settings for block mode."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType2=B
TagReadBlockNum=4
TagReadKeySlot=1
TagReadKeyType=A
TagReadOffset=0
TagReadLength=16
TagReadFormat=h
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.tag_read is not None
        assert config.nfc.tag_read.block_num == 4
        assert config.nfc.tag_read.key_slot == 1
        assert config.nfc.tag_read.key_type.value == "A"
        assert config.nfc.tag_read.offset == 0
        assert config.nfc.tag_read.length == 16
        assert config.nfc.tag_read.format.value == "h"

    def test_parse_nfc_tag_read_min_digits(self) -> None:
        """Parse TagReadMinDigits setting."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType2=U
TagReadMinDigits=10
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.tag_read is not None
        assert config.nfc.tag_read.min_digits == 10

    def test_parse_nfc_tag_read_min_digits_auto(self) -> None:
        """Parse TagReadMinDigits with auto value."""
        from vtap100.parser import parse

        content = """!VTAPconfig
NFCType2=U
TagReadMinDigits=A
"""
        config = parse(content)
        assert config.nfc is not None
        assert config.nfc.tag_read is not None
        assert config.nfc.tag_read.min_digits == "A"


class TestConfigParserDESFire:
    """Test DESFire configuration parsing."""

    def test_parse_single_desfire_app(self) -> None:
        """Parse single DESFire application."""
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=AABBCC
DESFire1FileID=1
DESFire1KeySlot=1
"""
        config = parse(content)
        assert config.desfire is not None
        assert len(config.desfire.apps) == 1
        assert config.desfire.apps[0].app_id == "AABBCC"
        assert config.desfire.apps[0].file_id == 1
        assert config.desfire.apps[0].key_slot == 1

    def test_parse_desfire_with_crypto(self) -> None:
        """Parse DESFire with crypto mode."""
        from vtap100.models.desfire import DESFireCryptoMode
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=112233
DESFire1Crypto=3
"""
        config = parse(content)
        assert config.desfire is not None
        assert config.desfire.apps[0].crypto == DESFireCryptoMode.AES

    def test_parse_desfire_with_format(self) -> None:
        """Parse DESFire with data format."""
        from vtap100.models.desfire import DESFireDataFormat
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=ABCDEF
DESFire1Format=2
"""
        config = parse(content)
        assert config.desfire is not None
        assert config.desfire.apps[0].format == DESFireDataFormat.KEYID_V2

    def test_parse_desfire_read_settings(self) -> None:
        """Parse DESFire read length and offset."""
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=123456
DESFire1ReadLength=16
DESFire1ReadOffset=4
"""
        config = parse(content)
        assert config.desfire is not None
        assert config.desfire.apps[0].read_length == 16
        assert config.desfire.apps[0].read_offset == 4

    def test_parse_desfire_diversification(self) -> None:
        """Parse DESFire with diversification enabled."""
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=AABBCC
DESFire1Diversification=1
"""
        config = parse(content)
        assert config.desfire is not None
        assert config.desfire.apps[0].diversification is True

    def test_parse_desfire_privacy_settings(self) -> None:
        """Parse DESFire privacy key settings."""
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=112233
DESFire1PrivacyKeyNum=2
DESFire1PrivacyKeySlot=3
"""
        config = parse(content)
        assert config.desfire is not None
        assert config.desfire.apps[0].privacy_key_num == 2
        assert config.desfire.apps[0].privacy_key_slot == 3

    def test_parse_desfire_sysid_settings(self) -> None:
        """Parse DESFire system ID settings."""
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=ABCDEF
DESFire1SysIDKeySlot=4
DESFire1SysIDLength=8
"""
        config = parse(content)
        assert config.desfire is not None
        assert config.desfire.apps[0].sysid_key_slot == 4
        assert config.desfire.apps[0].sysid_length == 8

    def test_parse_multiple_desfire_apps(self) -> None:
        """Parse multiple DESFire applications."""
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=AAAAAA
DESFire1KeySlot=1
DESFire2AppID=BBBBBB
DESFire2KeySlot=2
DESFire3AppID=CCCCCC
DESFire3KeySlot=3
"""
        config = parse(content)
        assert config.desfire is not None
        assert len(config.desfire.apps) == 3
        assert config.desfire.apps[0].app_id == "AAAAAA"
        assert config.desfire.apps[1].app_id == "BBBBBB"
        assert config.desfire.apps[2].app_id == "CCCCCC"

    def test_parse_desfire_separator(self) -> None:
        """Parse DESFire separator setting."""
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=AABBCC
DESFireSeparator=;
"""
        config = parse(content)
        assert config.desfire is not None
        assert config.desfire.separator == ";"

    def test_parse_desfire_key_num(self) -> None:
        """Parse DESFire key number."""
        from vtap100.parser import parse

        content = """!VTAPconfig
DESFire1AppID=123456
DESFire1KeyNum=5
"""
        config = parse(content)
        assert config.desfire is not None
        assert config.desfire.apps[0].key_num == 5


class TestConfigParserFeedback:
    """Test LED and Beep feedback configuration parsing."""

    def test_parse_led_mode(self) -> None:
        """Parse LED mode setting."""
        from vtap100.models.feedback import LEDMode
        from vtap100.parser import parse

        content = """!VTAPconfig
LEDMode=3
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.led is not None
        assert config.feedback.led.mode == LEDMode.CUSTOM

    def test_parse_led_select(self) -> None:
        """Parse LED select setting."""
        from vtap100.models.feedback import LEDSelect
        from vtap100.parser import parse

        content = """!VTAPconfig
LEDSelect=1
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.led is not None
        assert config.feedback.led.select == LEDSelect.ONBOARD_COMPACT

    def test_parse_led_default_rgb(self) -> None:
        """Parse LED default RGB color."""
        from vtap100.parser import parse

        content = """!VTAPconfig
LEDDefaultRGB=00FF00
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.led is not None
        assert config.feedback.led.default_rgb == "00FF00"

    def test_parse_pass_led_sequence(self) -> None:
        """Parse PassLED sequence."""
        from vtap100.parser import parse

        content = """!VTAPconfig
PassLED=00FF00,100,50,3
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.led is not None
        assert config.feedback.led.pass_led is not None
        assert config.feedback.led.pass_led.color == "00FF00"
        assert config.feedback.led.pass_led.on_ms == 100
        assert config.feedback.led.pass_led.off_ms == 50
        assert config.feedback.led.pass_led.repeats == 3

    def test_parse_tag_led_sequence(self) -> None:
        """Parse TagLED sequence."""
        from vtap100.parser import parse

        content = """!VTAPconfig
TagLED=0000FF,200,100,2
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.led is not None
        assert config.feedback.led.tag_led is not None
        assert config.feedback.led.tag_led.color == "0000FF"

    def test_parse_pass_error_led(self) -> None:
        """Parse PassErrorLED sequence."""
        from vtap100.parser import parse

        content = """!VTAPconfig
PassErrorLED=FF0000,50,50,5
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.led.pass_error_led is not None
        assert config.feedback.led.pass_error_led.color == "FF0000"

    def test_parse_start_led(self) -> None:
        """Parse StartLED sequence."""
        from vtap100.parser import parse

        content = """!VTAPconfig
StartLED=FFFFFF,500,0,1
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.led.start_led is not None
        assert config.feedback.led.start_led.color == "FFFFFF"

    def test_parse_pass_beep(self) -> None:
        """Parse PassBeep sequence."""
        from vtap100.parser import parse

        content = """!VTAPconfig
PassBeep=100,50,2
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.beep is not None
        assert config.feedback.beep.pass_beep is not None
        assert config.feedback.beep.pass_beep.on_ms == 100
        assert config.feedback.beep.pass_beep.off_ms == 50
        assert config.feedback.beep.pass_beep.repeats == 2

    def test_parse_pass_beep_with_frequency(self) -> None:
        """Parse PassBeep sequence with custom frequency."""
        from vtap100.parser import parse

        content = """!VTAPconfig
PassBeep=100,50,2,2000
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.beep.pass_beep is not None
        assert config.feedback.beep.pass_beep.frequency == 2000

    def test_parse_tag_beep(self) -> None:
        """Parse TagBeep sequence."""
        from vtap100.parser import parse

        content = """!VTAPconfig
TagBeep=150,75,1
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.beep.tag_beep is not None
        assert config.feedback.beep.tag_beep.on_ms == 150

    def test_parse_pass_error_beep(self) -> None:
        """Parse PassErrorBeep sequence."""
        from vtap100.parser import parse

        content = """!VTAPconfig
PassErrorBeep=50,25,3,1000
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.beep.pass_error_beep is not None
        assert config.feedback.beep.pass_error_beep.frequency == 1000

    def test_parse_start_beep(self) -> None:
        """Parse StartBeep sequence."""
        from vtap100.parser import parse

        content = """!VTAPconfig
StartBeep=200,0,1
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.beep.start_beep is not None
        assert config.feedback.beep.start_beep.on_ms == 200

    def test_parse_combined_feedback(self) -> None:
        """Parse combined LED and beep settings."""
        from vtap100.parser import parse

        content = """!VTAPconfig
LEDMode=3
PassLED=00FF00,100,50,2
PassBeep=100,50,1
"""
        config = parse(content)
        assert config.feedback is not None
        assert config.feedback.led is not None
        assert config.feedback.beep is not None


class TestConfigParserNFCRoundTrip:
    """Test NFC config generate -> parse roundtrip."""

    def test_roundtrip_nfc_basic(self) -> None:
        """Generate and parse NFC config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.nfc import NFCTagConfig
        from vtap100.models.nfc import NFCTagMode
        from vtap100.parser import parse

        original = VTAPConfig(nfc=NFCTagConfig(type2=NFCTagMode.UID, type4=NFCTagMode.NDEF))
        generator = ConfigGenerator(original)
        content = generator.generate()
        parsed = parse(content)

        assert parsed.nfc is not None
        assert parsed.nfc.type2 == original.nfc.type2
        assert parsed.nfc.type4 == original.nfc.type4


class TestConfigParserDESFireRoundTrip:
    """Test DESFire config generate -> parse roundtrip."""

    def test_roundtrip_desfire_basic(self) -> None:
        """Generate and parse DESFire config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig
        from vtap100.parser import parse

        original = VTAPConfig(
            desfire=DESFireConfig(apps=[DESFireAppConfig(app_id="AABBCC", key_slot=1, file_id=1)])
        )
        generator = ConfigGenerator(original)
        content = generator.generate()
        parsed = parse(content)

        assert parsed.desfire is not None
        assert len(parsed.desfire.apps) == 1
        assert parsed.desfire.apps[0].app_id == original.desfire.apps[0].app_id


class TestConfigParserFeedbackRoundTrip:
    """Test Feedback config generate -> parse roundtrip."""

    def test_roundtrip_feedback_led(self) -> None:
        """Generate and parse LED feedback config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.feedback import FeedbackConfig
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDMode
        from vtap100.models.feedback import LEDSequence
        from vtap100.parser import parse

        original = VTAPConfig(
            feedback=FeedbackConfig(
                led=LEDConfig(
                    mode=LEDMode.CUSTOM,
                    pass_led=LEDSequence(color="00FF00", on_ms=100, off_ms=50, repeats=2),
                )
            )
        )
        generator = ConfigGenerator(original)
        content = generator.generate()
        parsed = parse(content)

        assert parsed.feedback is not None
        assert parsed.feedback.led is not None
        assert parsed.feedback.led.mode == LEDMode.CUSTOM
        assert parsed.feedback.led.pass_led is not None
        assert parsed.feedback.led.pass_led.color == "00FF00"


class TestSlotPreservation:
    """Pass slot numbers must survive parse and regenerate."""

    def test_vas_slot_is_captured(self) -> None:
        """VAS2 stays slot 2 in the model."""
        from vtap100.parser import parse

        config = parse("!VTAPconfig\nVAS2MerchantID=pass.com.example.x\nVAS2KeySlot=2\n")
        assert config.vas_configs[0].slot == 2

    def test_smarttap_slot_is_captured(self) -> None:
        """ST3 stays slot 3 in the model."""
        from vtap100.parser import parse

        config = parse("!VTAPconfig\nST3CollectorID=12345678\nST3KeySlot=3\n")
        assert config.smarttap_configs[0].slot == 3

    def test_slots_are_not_renumbered(self) -> None:
        """Regenerating writes back the original slot numbers."""
        from vtap100.generator import ConfigGenerator
        from vtap100.parser import parse

        text = "!VTAPconfig\nVAS2MerchantID=pass.com.example.x\nST3CollectorID=12345678\n"
        out = ConfigGenerator(parse(text)).generate()
        assert "VAS2MerchantID" in out
        assert "ST3CollectorID" in out
        assert "VAS1MerchantID" not in out
        assert "ST2CollectorID" not in out

    def test_smarttap_slot_one_is_preserved(self) -> None:
        """ST1 is written back as ST1, not silently moved to ST2.

        ST1 does not work on real readers (see d18c8c4) and config creation
        still avoids it, but rewriting a file the user asked us to load is a
        silent change to their configuration.
        """
        from vtap100.generator import ConfigGenerator
        from vtap100.parser import parse

        out = ConfigGenerator(parse("!VTAPconfig\nST1CollectorID=80644855\n")).generate()
        assert "ST1CollectorID=80644855" in out
