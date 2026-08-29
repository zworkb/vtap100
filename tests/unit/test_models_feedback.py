"""Unit tests for LED and Beep feedback configuration models.

TDD Red Phase: These tests define the expected behavior of the FeedbackConfig model.
Tests should fail until the implementation is complete.

Phase 5 focuses on LED and Beep/Buzzer settings.
"""

from pydantic import ValidationError
import pytest


class TestLEDMode:
    """Tests for LEDMode enum."""

    def test_led_mode_off(self) -> None:
        """Mode 0 means LEDs off."""
        from vtap100.models.feedback import LEDMode

        assert LEDMode.OFF.value == 0

    def test_led_mode_on(self) -> None:
        """Mode 1 means LEDs on."""
        from vtap100.models.feedback import LEDMode

        assert LEDMode.ON.value == 1

    def test_led_mode_status(self) -> None:
        """Mode 2 means status indicator."""
        from vtap100.models.feedback import LEDMode

        assert LEDMode.STATUS.value == 2

    def test_led_mode_custom(self) -> None:
        """Mode 3 means custom sequences."""
        from vtap100.models.feedback import LEDMode

        assert LEDMode.CUSTOM.value == 3


class TestLEDSelect:
    """Tests for LEDSelect enum."""

    def test_led_select_external(self) -> None:
        """Select 0 means external RGB LED."""
        from vtap100.models.feedback import LEDSelect

        assert LEDSelect.EXTERNAL.value == 0

    def test_led_select_onboard_compact(self) -> None:
        """Select 1 means on-board LED (compact case)."""
        from vtap100.models.feedback import LEDSelect

        assert LEDSelect.ONBOARD_COMPACT.value == 1

    def test_led_select_onboard_square(self) -> None:
        """Select 2 means on-board LED (square case)."""
        from vtap100.models.feedback import LEDSelect

        assert LEDSelect.ONBOARD_SQUARE.value == 2

    def test_led_select_serial(self) -> None:
        """Select 3 means serial LEDs."""
        from vtap100.models.feedback import LEDSelect

        assert LEDSelect.SERIAL.value == 3


class TestLEDSequence:
    """Tests for LEDSequence model (color,on,off,repeats)."""

    def test_led_sequence_defaults(self) -> None:
        """Trailing sequence fields are absent unless the file sets them.

        The manufacturer documents omitting them, and its own TagLED example
        is two-valued, so a short form must round-trip as a short form.
        """
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="00FF00")
        assert seq.color == "00FF00"
        assert seq.on_ms == 100
        assert seq.off_ms is None
        assert seq.repeats is None

    def test_led_sequence_color_required(self) -> None:
        """Color is required."""
        from vtap100.models.feedback import LEDSequence

        with pytest.raises(ValidationError):
            LEDSequence()

    def test_led_sequence_color_hex_format(self) -> None:
        """Color must be 6 hex characters."""
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="FF0000", on_ms=100, off_ms=100, repeats=1)
        assert seq.color == "FF0000"

        seq = LEDSequence(color="00ff00", on_ms=100, off_ms=100, repeats=1)
        assert seq.color == "00FF00"  # Should be uppercased

    def test_led_sequence_color_invalid_length(self) -> None:
        """Color with invalid length should fail."""
        from vtap100.models.feedback import LEDSequence

        with pytest.raises(ValidationError):
            LEDSequence(color="FF00")

    def test_led_sequence_color_invalid_hex(self) -> None:
        """Color with invalid hex characters should fail."""
        from vtap100.models.feedback import LEDSequence

        with pytest.raises(ValidationError):
            LEDSequence(color="GGHHII")

    def test_led_sequence_on_ms_range(self) -> None:
        """On time must be 0-65535."""
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="00FF00", on_ms=0)
        assert seq.on_ms == 0

        seq = LEDSequence(color="00FF00", on_ms=65535)
        assert seq.on_ms == 65535

    def test_led_sequence_on_ms_invalid(self) -> None:
        """On time above 65535 should fail."""
        from vtap100.models.feedback import LEDSequence

        with pytest.raises(ValidationError):
            LEDSequence(color="00FF00", on_ms=65536)

    def test_led_sequence_off_ms_range(self) -> None:
        """Off time must be 0-65535."""
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="00FF00", off_ms=0)
        assert seq.off_ms == 0

        seq = LEDSequence(color="00FF00", off_ms=65535)
        assert seq.off_ms == 65535

    def test_led_sequence_repeats_range(self) -> None:
        """Repeats must be 1-255."""
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="00FF00", repeats=1)
        assert seq.repeats == 1

        seq = LEDSequence(color="00FF00", repeats=255)
        assert seq.repeats == 255

    def test_led_sequence_repeats_zero_invalid(self) -> None:
        """Repeats 0 should fail."""
        from vtap100.models.feedback import LEDSequence

        with pytest.raises(ValidationError):
            LEDSequence(color="00FF00", repeats=0)

    def test_led_sequence_to_config_value(self) -> None:
        """Should generate correct config value format."""
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="00FF00", on_ms=100, off_ms=100, repeats=2)
        assert seq.to_config_value() == "00FF00,100,100,2"

    def test_led_sequence_to_config_value_custom(self) -> None:
        """Should generate correct config value with custom values."""
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="FF0000", on_ms=200, off_ms=50, repeats=5)
        assert seq.to_config_value() == "FF0000,200,50,5"


class TestBeepSequence:
    """Tests for BeepSequence model (on,off,repeats[,freq])."""

    def test_beep_sequence_defaults(self) -> None:
        """Trailing sequence fields are absent unless the file sets them."""
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence()
        assert seq.on_ms == 100
        assert seq.off_ms is None
        assert seq.repeats is None
        assert seq.frequency is None

    def test_beep_sequence_on_ms_range(self) -> None:
        """On time must be 0-65535."""
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(on_ms=0)
        assert seq.on_ms == 0

        seq = BeepSequence(on_ms=65535)
        assert seq.on_ms == 65535

    def test_beep_sequence_on_ms_invalid(self) -> None:
        """On time above 65535 should fail."""
        from vtap100.models.feedback import BeepSequence

        with pytest.raises(ValidationError):
            BeepSequence(on_ms=65536)

    def test_beep_sequence_off_ms_range(self) -> None:
        """Off time must be 0-65535."""
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(off_ms=0)
        assert seq.off_ms == 0

        seq = BeepSequence(off_ms=65535)
        assert seq.off_ms == 65535

    def test_beep_sequence_repeats_range(self) -> None:
        """Repeats must be 1-255."""
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(repeats=1)
        assert seq.repeats == 1

        seq = BeepSequence(repeats=255)
        assert seq.repeats == 255

    def test_beep_sequence_repeats_zero_invalid(self) -> None:
        """Repeats 0 should fail."""
        from vtap100.models.feedback import BeepSequence

        with pytest.raises(ValidationError):
            BeepSequence(repeats=0)

    def test_beep_sequence_frequency(self) -> None:
        """Can set custom frequency."""
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(frequency=2000)
        assert seq.frequency == 2000

    def test_beep_sequence_frequency_range(self) -> None:
        """Frequency must be 100-20000."""
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(frequency=100)
        assert seq.frequency == 100

        seq = BeepSequence(frequency=20000)
        assert seq.frequency == 20000

    def test_beep_sequence_frequency_below_min_invalid(self) -> None:
        """Frequency below 100 should fail."""
        from vtap100.models.feedback import BeepSequence

        with pytest.raises(ValidationError):
            BeepSequence(frequency=99)

    def test_beep_sequence_to_config_value_basic(self) -> None:
        """Should generate correct config value without frequency."""
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(on_ms=100, off_ms=100, repeats=2)
        assert seq.to_config_value() == "100,100,2"

    def test_beep_sequence_to_config_value_with_frequency(self) -> None:
        """Should generate correct config value with frequency."""
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(on_ms=100, off_ms=100, repeats=2, frequency=3136)
        assert seq.to_config_value() == "100,100,2,3136"


class TestLEDConfig:
    """Tests for LEDConfig model."""

    def test_led_config_defaults(self) -> None:
        """LED config should have sensible defaults."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSelect

        config = LEDConfig()
        assert config.mode is None
        assert config.select == LEDSelect.ONBOARD_COMPACT  # Default: on-board LED (compact case)
        assert config.default_rgb is None
        assert config.pass_led is None
        assert config.tag_led is None
        assert config.pass_error_led is None
        assert config.start_led is None

    def test_led_config_mode(self) -> None:
        """Can set LED mode."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDMode

        config = LEDConfig(mode=LEDMode.ON)
        assert config.mode == LEDMode.ON

    def test_led_config_select(self) -> None:
        """Can set LED select."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSelect

        config = LEDConfig(select=LEDSelect.EXTERNAL)
        assert config.select == LEDSelect.EXTERNAL

    def test_led_config_default_rgb(self) -> None:
        """Can set default RGB color."""
        from vtap100.models.feedback import LEDConfig

        config = LEDConfig(default_rgb="00FF00")
        assert config.default_rgb == "00FF00"

    def test_led_config_default_rgb_validation(self) -> None:
        """Default RGB must be 6 hex characters."""
        from vtap100.models.feedback import LEDConfig

        with pytest.raises(ValidationError):
            LEDConfig(default_rgb="invalid")

    def test_led_config_default_rgb_invalid_hex(self) -> None:
        """Default RGB with invalid hex characters should fail."""
        from vtap100.models.feedback import LEDConfig

        with pytest.raises(ValidationError):
            LEDConfig(default_rgb="GGHHII")

    def test_led_config_pass_led(self) -> None:
        """Can set pass LED sequence."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="00FF00", on_ms=100, off_ms=100, repeats=2)
        config = LEDConfig(pass_led=seq)
        assert config.pass_led == seq

    def test_led_config_tag_led(self) -> None:
        """Can set tag LED sequence."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="0000FF", on_ms=100, off_ms=100, repeats=1)
        config = LEDConfig(tag_led=seq)
        assert config.tag_led == seq

    def test_led_config_pass_error_led(self) -> None:
        """Can set pass error LED sequence."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="FF0000", on_ms=100, off_ms=100, repeats=1)
        config = LEDConfig(pass_error_led=seq)
        assert config.pass_error_led == seq

    def test_led_config_start_led(self) -> None:
        """Can set start LED sequence."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSequence

        seq = LEDSequence(color="FFFF00", on_ms=100, off_ms=100, repeats=1)
        config = LEDConfig(start_led=seq)
        assert config.start_led == seq


class TestBeepConfig:
    """Tests for BeepConfig model."""

    def test_beep_config_defaults(self) -> None:
        """Beep config should have sensible defaults."""
        from vtap100.models.feedback import BeepConfig

        config = BeepConfig()
        assert config.pass_beep is None
        assert config.tag_beep is None
        assert config.pass_error_beep is None
        assert config.start_beep is None

    def test_beep_config_pass_beep(self) -> None:
        """Can set pass beep sequence."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(on_ms=100, off_ms=100, repeats=2)
        config = BeepConfig(pass_beep=seq)
        assert config.pass_beep == seq

    def test_beep_config_tag_beep(self) -> None:
        """Can set tag beep sequence."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(on_ms=50, off_ms=50, repeats=1)
        config = BeepConfig(tag_beep=seq)
        assert config.tag_beep == seq

    def test_beep_config_pass_error_beep(self) -> None:
        """Can set pass error beep sequence."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(on_ms=200, off_ms=100, repeats=3)
        config = BeepConfig(pass_error_beep=seq)
        assert config.pass_error_beep == seq

    def test_beep_config_start_beep(self) -> None:
        """Can set start beep sequence."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        seq = BeepSequence(on_ms=500, off_ms=0, repeats=1)
        config = BeepConfig(start_beep=seq)
        assert config.start_beep == seq


class TestFeedbackConfig:
    """Tests for combined FeedbackConfig model."""

    def test_feedback_config_defaults(self) -> None:
        """Feedback config should have sensible defaults."""
        from vtap100.models.feedback import FeedbackConfig

        config = FeedbackConfig()
        assert config.led is None
        assert config.beep is None

    def test_feedback_config_with_led(self) -> None:
        """Can set LED config."""
        from vtap100.models.feedback import FeedbackConfig
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDMode

        led = LEDConfig(mode=LEDMode.ON)
        config = FeedbackConfig(led=led)
        assert config.led == led

    def test_feedback_config_with_beep(self) -> None:
        """Can set beep config."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence
        from vtap100.models.feedback import FeedbackConfig

        beep = BeepConfig(pass_beep=BeepSequence(on_ms=100, off_ms=100, repeats=1))
        config = FeedbackConfig(beep=beep)
        assert config.beep == beep


class TestLEDConfigOutput:
    """Tests for LEDConfig config.txt output generation."""

    def test_to_config_lines_default(self) -> None:
        """Default LED config should generate LEDSelect line."""
        from vtap100.models.feedback import LEDConfig

        config = LEDConfig()
        lines = config.to_config_lines()
        # Default LEDSelect=1 (ONBOARD_COMPACT) is always set
        assert lines == ["LEDSelect=1"]

    def test_to_config_lines_mode(self) -> None:
        """Mode should generate LEDMode line."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDMode

        config = LEDConfig(mode=LEDMode.ON)
        lines = config.to_config_lines()
        assert "LEDMode=1" in lines

    def test_to_config_lines_select(self) -> None:
        """Select should generate LEDSelect line."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSelect

        config = LEDConfig(select=LEDSelect.EXTERNAL)
        lines = config.to_config_lines()
        assert "LEDSelect=0" in lines

    def test_to_config_lines_default_rgb(self) -> None:
        """Default RGB should generate LEDDefaultRGB line."""
        from vtap100.models.feedback import LEDConfig

        config = LEDConfig(default_rgb="00FF00")
        lines = config.to_config_lines()
        assert "LEDDefaultRGB=00FF00" in lines

    def test_to_config_lines_pass_led(self) -> None:
        """Pass LED should generate PassLED line."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSequence

        config = LEDConfig(pass_led=LEDSequence(color="00FF00", on_ms=100, off_ms=100, repeats=2))
        lines = config.to_config_lines()
        assert "PassLED=00FF00,100,100,2" in lines

    def test_to_config_lines_tag_led(self) -> None:
        """Tag LED should generate TagLED line."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSequence

        config = LEDConfig(tag_led=LEDSequence(color="0000FF", on_ms=100, off_ms=100, repeats=1))
        lines = config.to_config_lines()
        assert "TagLED=0000FF,100,100,1" in lines

    def test_to_config_lines_pass_error_led(self) -> None:
        """Pass error LED should generate PassErrorLED line."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSequence

        config = LEDConfig(
            pass_error_led=LEDSequence(color="FF0000", on_ms=100, off_ms=100, repeats=1)
        )
        lines = config.to_config_lines()
        assert "PassErrorLED=FF0000,100,100,1" in lines

    def test_to_config_lines_start_led(self) -> None:
        """Start LED should generate StartLED line."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDSequence

        config = LEDConfig(start_led=LEDSequence(color="FFFF00", on_ms=100, off_ms=100, repeats=1))
        lines = config.to_config_lines()
        assert "StartLED=FFFF00,100,100,1" in lines

    def test_to_config_lines_full_config(self) -> None:
        """Full LED config should generate all lines."""
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDMode
        from vtap100.models.feedback import LEDSelect
        from vtap100.models.feedback import LEDSequence

        config = LEDConfig(
            mode=LEDMode.CUSTOM,
            select=LEDSelect.ONBOARD_COMPACT,
            default_rgb="FFFFFF",
            pass_led=LEDSequence(color="00FF00", on_ms=100, off_ms=100, repeats=2),
            tag_led=LEDSequence(color="0000FF", on_ms=100, off_ms=100, repeats=1),
            pass_error_led=LEDSequence(color="FF0000", on_ms=200, off_ms=100, repeats=3),
            start_led=LEDSequence(color="FFFF00", on_ms=100, off_ms=100, repeats=1),
        )
        lines = config.to_config_lines()

        assert "LEDMode=3" in lines
        assert "LEDSelect=1" in lines
        assert "LEDDefaultRGB=FFFFFF" in lines
        assert "PassLED=00FF00,100,100,2" in lines
        assert "TagLED=0000FF,100,100,1" in lines
        assert "PassErrorLED=FF0000,200,100,3" in lines
        assert "StartLED=FFFF00,100,100,1" in lines


class TestBeepConfigOutput:
    """Tests for BeepConfig config.txt output generation."""

    def test_to_config_lines_empty(self) -> None:
        """Empty beep config should generate no lines."""
        from vtap100.models.feedback import BeepConfig

        config = BeepConfig()
        lines = config.to_config_lines()
        assert lines == []

    def test_to_config_lines_pass_beep(self) -> None:
        """Pass beep should generate PassBeep line."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        config = BeepConfig(pass_beep=BeepSequence(on_ms=100, off_ms=100, repeats=2))
        lines = config.to_config_lines()
        assert "PassBeep=100,100,2" in lines

    def test_to_config_lines_pass_beep_with_frequency(self) -> None:
        """Pass beep with frequency should include it."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        config = BeepConfig(
            pass_beep=BeepSequence(on_ms=100, off_ms=100, repeats=2, frequency=3136)
        )
        lines = config.to_config_lines()
        assert "PassBeep=100,100,2,3136" in lines

    def test_to_config_lines_tag_beep(self) -> None:
        """Tag beep should generate TagBeep line."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        config = BeepConfig(tag_beep=BeepSequence(on_ms=100, off_ms=100, repeats=1))
        lines = config.to_config_lines()
        assert "TagBeep=100,100,1" in lines

    def test_to_config_lines_pass_error_beep(self) -> None:
        """Pass error beep should generate PassErrorBeep line."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        config = BeepConfig(pass_error_beep=BeepSequence(on_ms=200, off_ms=100, repeats=3))
        lines = config.to_config_lines()
        assert "PassErrorBeep=200,100,3" in lines

    def test_to_config_lines_start_beep(self) -> None:
        """Start beep should generate StartBeep line."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        config = BeepConfig(start_beep=BeepSequence(on_ms=500, off_ms=0, repeats=1))
        lines = config.to_config_lines()
        assert "StartBeep=500,0,1" in lines

    def test_to_config_lines_full_config(self) -> None:
        """Full beep config should generate all lines."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence

        config = BeepConfig(
            pass_beep=BeepSequence(on_ms=100, off_ms=100, repeats=2),
            tag_beep=BeepSequence(on_ms=50, off_ms=50, repeats=1),
            pass_error_beep=BeepSequence(on_ms=200, off_ms=100, repeats=3, frequency=2000),
            start_beep=BeepSequence(on_ms=500, off_ms=0, repeats=1),
        )
        lines = config.to_config_lines()

        assert "PassBeep=100,100,2" in lines
        assert "TagBeep=50,50,1" in lines
        assert "PassErrorBeep=200,100,3,2000" in lines
        assert "StartBeep=500,0,1" in lines


class TestFeedbackConfigOutput:
    """Tests for FeedbackConfig config.txt output generation."""

    def test_to_config_lines_empty(self) -> None:
        """Empty feedback config should generate no lines."""
        from vtap100.models.feedback import FeedbackConfig

        config = FeedbackConfig()
        lines = config.to_config_lines()
        assert lines == []

    def test_to_config_lines_led_only(self) -> None:
        """LED only config should generate LED lines."""
        from vtap100.models.feedback import FeedbackConfig
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDMode

        config = FeedbackConfig(led=LEDConfig(mode=LEDMode.ON))
        lines = config.to_config_lines()
        assert "LEDMode=1" in lines

    def test_to_config_lines_beep_only(self) -> None:
        """Beep only config should generate beep lines."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence
        from vtap100.models.feedback import FeedbackConfig

        config = FeedbackConfig(
            beep=BeepConfig(pass_beep=BeepSequence(on_ms=100, off_ms=100, repeats=1))
        )
        lines = config.to_config_lines()
        assert "PassBeep=100,100,1" in lines

    def test_to_config_lines_combined(self) -> None:
        """Combined config should generate all lines."""
        from vtap100.models.feedback import BeepConfig
        from vtap100.models.feedback import BeepSequence
        from vtap100.models.feedback import FeedbackConfig
        from vtap100.models.feedback import LEDConfig
        from vtap100.models.feedback import LEDMode
        from vtap100.models.feedback import LEDSequence

        config = FeedbackConfig(
            led=LEDConfig(
                mode=LEDMode.ON,
                pass_led=LEDSequence(color="00FF00", on_ms=100, off_ms=100, repeats=1),
            ),
            beep=BeepConfig(pass_beep=BeepSequence(on_ms=100, off_ms=100, repeats=1)),
        )
        lines = config.to_config_lines()

        assert "LEDMode=1" in lines
        assert "PassLED=00FF00,100,100,1" in lines
        assert "PassBeep=100,100,1" in lines
