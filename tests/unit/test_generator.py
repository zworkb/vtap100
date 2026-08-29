"""Unit tests for config.txt generator.

TDD Red Phase: These tests define the expected behavior of the config generator.
Tests should fail until the implementation is complete.
"""

from io import StringIO
from pathlib import Path


class TestVTAPConfig:
    """Tests for VTAPConfig main configuration model."""

    def test_vtap_config_empty(self) -> None:
        """Empty config should be valid."""
        from vtap100.models.config import VTAPConfig

        config = VTAPConfig()
        assert config.vas_configs == []
        assert config.smarttap_configs == []

    def test_vtap_config_with_vas(self) -> None:
        """Config with VAS should store configs."""
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig

        vas = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        config = VTAPConfig(vas_configs=[vas])

        assert len(config.vas_configs) == 1
        assert config.vas_configs[0].merchant_id == "pass.com.example.test"

    def test_vtap_config_with_smarttap(self) -> None:
        """Config with Smart Tap should store configs."""
        from vtap100.models.config import VTAPConfig
        from vtap100.models.smarttap import GoogleSmartTapConfig

        st = GoogleSmartTapConfig(slot=2, collector_id="96972794", key_slot=2)
        config = VTAPConfig(smarttap_configs=[st])

        assert len(config.smarttap_configs) == 1
        assert config.smarttap_configs[0].collector_id == "96972794"

    def test_vtap_config_with_keyboard(self) -> None:
        """Config with keyboard settings should store config."""
        from vtap100.models.config import VTAPConfig
        from vtap100.models.keyboard import KeyboardConfig

        kb = KeyboardConfig(log_mode=True, source="A1")
        config = VTAPConfig(keyboard=kb)

        assert config.keyboard is not None
        assert config.keyboard.log_mode is True

    def test_vtap_config_combined(self) -> None:
        """Config can have VAS, Smart Tap, and keyboard together."""
        from vtap100.models.config import VTAPConfig
        from vtap100.models.keyboard import KeyboardConfig
        from vtap100.models.smarttap import GoogleSmartTapConfig
        from vtap100.models.vas import AppleVASConfig

        vas = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        st = GoogleSmartTapConfig(slot=2, collector_id="96972794", key_slot=2)
        kb = KeyboardConfig(log_mode=True, source="AG")

        config = VTAPConfig(
            vas_configs=[vas],
            smarttap_configs=[st],
            keyboard=kb,
        )

        assert len(config.vas_configs) == 1
        assert len(config.smarttap_configs) == 1
        assert config.keyboard is not None


class TestConfigGenerator:
    """Tests for config.txt file generator."""

    def test_generate_header(self) -> None:
        """Generated config should start with !VTAPconfig."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig

        config = VTAPConfig()
        generator = ConfigGenerator(config)
        output = generator.generate()

        assert output.startswith("!VTAPconfig")

    def test_generate_with_comment(self) -> None:
        """Generated config can include a comment."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig

        config = VTAPConfig()
        generator = ConfigGenerator(config)
        output = generator.generate(comment="Test configuration")

        assert "!VTAPconfig" in output
        assert "; Test configuration" in output

    def test_generate_vas_only(self) -> None:
        """Generate config with only Apple VAS."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig

        vas = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        config = VTAPConfig(vas_configs=[vas])
        generator = ConfigGenerator(config)
        output = generator.generate()

        assert "VAS1MerchantID=pass.com.example.test" in output
        assert "VAS1KeySlot=1" in output

    def test_generate_smarttap_only(self) -> None:
        """Generate config with only Google Smart Tap."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.smarttap import GoogleSmartTapConfig

        st = GoogleSmartTapConfig(slot=2, collector_id="96972794", key_slot=2, key_version=1)
        config = VTAPConfig(smarttap_configs=[st])
        generator = ConfigGenerator(config)
        output = generator.generate()

        # ST1 does not work, generator starts at ST2
        assert "ST2CollectorID=96972794" in output
        assert "ST2KeySlot=2" in output
        assert "ST2KeyVersion=1" in output

    def test_generate_keyboard_settings(self) -> None:
        """Generate config with keyboard settings."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.keyboard import KeyboardConfig

        kb = KeyboardConfig(log_mode=True, source="A1")
        config = VTAPConfig(keyboard=kb)
        generator = ConfigGenerator(config)
        output = generator.generate()

        assert "KBLogMode=1" in output
        assert "KBSource=A1" in output

    def test_generate_combined(self) -> None:
        """Generate config with VAS, Smart Tap, and keyboard."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.keyboard import KeyboardConfig
        from vtap100.models.smarttap import GoogleSmartTapConfig
        from vtap100.models.vas import AppleVASConfig

        vas = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        st = GoogleSmartTapConfig(slot=2, collector_id="96972794", key_slot=2, key_version=1)
        kb = KeyboardConfig(log_mode=True, source="AG")

        config = VTAPConfig(
            vas_configs=[vas],
            smarttap_configs=[st],
            keyboard=kb,
        )
        generator = ConfigGenerator(config)
        output = generator.generate()

        # Check all components present
        assert "!VTAPconfig" in output
        assert "VAS1MerchantID=pass.com.example.test" in output
        # ST1 does not work, generator starts at ST2
        assert "ST2CollectorID=96972794" in output
        assert "KBLogMode=1" in output

    def test_generate_multiple_vas(self) -> None:
        """Generate config with multiple VAS configurations."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig

        vas1 = AppleVASConfig(slot=1, merchant_id="pass.com.example.one", key_slot=1)
        vas2 = AppleVASConfig(slot=2, merchant_id="pass.com.example.two", key_slot=2)
        config = VTAPConfig(vas_configs=[vas1, vas2])
        generator = ConfigGenerator(config)
        output = generator.generate()

        assert "VAS1MerchantID=pass.com.example.one" in output
        assert "VAS1KeySlot=1" in output
        assert "VAS2MerchantID=pass.com.example.two" in output
        assert "VAS2KeySlot=2" in output


class TestConfigGeneratorFile:
    """Tests for writing config to file."""

    def test_write_to_file(self, tmp_path: Path) -> None:
        """Can write config to a file."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig

        vas = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        config = VTAPConfig(vas_configs=[vas])
        generator = ConfigGenerator(config)

        output_file = tmp_path / "config.txt"
        generator.write_to_file(output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "!VTAPconfig" in content
        assert "VAS1MerchantID=pass.com.example.test" in content

    def test_write_to_stringio(self) -> None:
        """Can write config to a StringIO object."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig

        vas = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        config = VTAPConfig(vas_configs=[vas])
        generator = ConfigGenerator(config)

        buffer = StringIO()
        generator.write_to_stream(buffer)

        content = buffer.getvalue()
        assert "!VTAPconfig" in content
        assert "VAS1MerchantID=pass.com.example.test" in content


class TestTemplateGeneration:
    """Tests for Jinja2 template generation."""

    def test_generate_template_excludes_vas(self) -> None:
        """Template mode should exclude VAS configs."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig

        vas = AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)
        config = VTAPConfig(vas_configs=[vas])
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        assert "VAS1MerchantID" not in result
        assert "{% for passinfo in passes %}" in result

    def test_generate_template_excludes_smarttap(self) -> None:
        """Template mode should exclude SmartTap configs."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.smarttap import GoogleSmartTapConfig

        st = GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=1)
        config = VTAPConfig(smarttap_configs=[st])
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        assert "ST1CollectorID" not in result

    def test_generate_template_includes_keyboard(self) -> None:
        """Template mode should include keyboard config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.keyboard import KeyboardConfig

        kb = KeyboardConfig(log_mode=True, source="AG")
        config = VTAPConfig(keyboard=kb)
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        assert "KBLogMode=1" in result
        assert "KBSource=AG" in result

    def test_generate_template_includes_nfc(self) -> None:
        """Template mode should include NFC config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.nfc import NFCTagConfig
        from vtap100.models.nfc import NFCTagMode

        nfc = NFCTagConfig(type2=NFCTagMode.UID)
        config = VTAPConfig(nfc=nfc)
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        assert "NFCType2=U" in result

    def test_generate_template_includes_desfire(self) -> None:
        """Template mode should include DESFire config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.desfire import DESFireAppConfig
        from vtap100.models.desfire import DESFireConfig

        app = DESFireAppConfig(app_id="AABBCC")
        desfire = DESFireConfig(apps=[app])
        config = VTAPConfig(desfire=desfire)
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        assert "DESFire1AppID=AABBCC" in result

    def test_generate_template_includes_feedback(self) -> None:
        """Template mode should include LED/Beep config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.feedback import FeedbackConfig
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDMode

        led = LEDConfig(mode=LEDMode.CUSTOM)
        feedback = FeedbackConfig(led=led)
        config = VTAPConfig(feedback=feedback)
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        assert "LEDMode=3" in result

    def test_generate_template_includes_jinja_placeholder(self) -> None:
        """Template mode should include Jinja2 placeholder."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig

        config = VTAPConfig()
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        assert "{% for passinfo in passes %}" in result
        assert "{% if passinfo.apple %}" in result
        assert "{% if passinfo.google %}" in result
        assert "{% endfor %}" in result

    def test_generate_template_has_correct_structure(self) -> None:
        """Template should have passes section before static config."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig
        from vtap100.models.keyboard import KeyboardConfig

        kb = KeyboardConfig(log_mode=True)
        config = VTAPConfig(keyboard=kb)
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        # Jinja block should come before keyboard config
        jinja_pos = result.find("{% for passinfo")
        kb_pos = result.find("KBLogMode")
        assert jinja_pos < kb_pos

    def test_generate_template_has_header(self) -> None:
        """Template should start with !VTAPconfig header."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig

        config = VTAPConfig()
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        assert result.startswith("!VTAPconfig")

    def test_generate_template_with_comment(self) -> None:
        """Template can include a comment."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig

        config = VTAPConfig()
        generator = ConfigGenerator(config)

        result = generator.generate_template(comment="Template for Phil")

        assert "; Template for Phil" in result

    def test_generate_template_jinja_vars_correct(self) -> None:
        """Jinja template should use correct variable names."""
        from vtap100.generator import ConfigGenerator
        from vtap100.models.config import VTAPConfig

        config = VTAPConfig()
        generator = ConfigGenerator(config)

        result = generator.generate_template()

        # Check Apple VAS variables
        assert "{{ passinfo.apple.merchant_id }}" in result
        assert "{{ passinfo.slot }}" in result
        # Check Google SmartTap variables
        assert "{{ passinfo.google.collector_id }}" in result
