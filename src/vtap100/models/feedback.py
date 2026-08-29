"""LED and Beep feedback configuration models for VTAP100 NFC reader.

This module provides models for configuring LED and buzzer feedback
on the VTAP100 NFC reader.

Phase 5 Implementation.
"""

from enum import IntEnum
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class LEDMode(IntEnum):
    """LED operating modes."""

    OFF = 0  # LEDs off
    ON = 1  # LEDs on
    STATUS = 2  # Status indicator
    CUSTOM = 3  # Custom sequences


class LEDSelect(IntEnum):
    """LED type/position selection."""

    EXTERNAL = 0  # External RGB LED (common cathode)
    ONBOARD_COMPACT = 1  # On-board LED (compact case)
    ONBOARD_SQUARE = 2  # On-board LED (square case)
    SERIAL = 3  # Serial LEDs


class LEDSequence(BaseModel):
    """LED sequence configuration (color, timing, repeats).

    Attributes:
        color: RGB color in hex format (6 characters, e.g., "00FF00").
        on_ms: On time in milliseconds (0-65535).
        off_ms: Off time in milliseconds (0-65535).
        repeats: Number of repeats (1-255).
    """

    color: str = Field(..., description="RGB color (6 hex chars)")
    on_ms: int = Field(default=100, ge=0, le=65535, description="On time in ms")
    off_ms: int | None = Field(default=None, ge=0, le=65535, description="Off time in ms")
    repeats: int | None = Field(default=None, ge=1, le=255, description="Number of repeats")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate color is 6 hex characters."""
        if len(v) != 6:
            msg = "Color must be 6 hex characters"
            raise ValueError(msg)
        # Validate hex format
        try:
            int(v, 16)
        except ValueError:
            msg = "Color must be valid hex"
            raise ValueError(msg) from None
        return v.upper()

    def to_config_value(self) -> str:
        """Generate config value: color,on[,off[,repeats]].

        Trailing parameters may be omitted, which the manufacturer documents
        and its own TagLED example uses. A short form is written back short.
        """
        parts = [self.color, str(self.on_ms)]
        if self.off_ms is not None:
            parts.append(str(self.off_ms))
            if self.repeats is not None:
                parts.append(str(self.repeats))
        return ",".join(parts)


class BeepSequence(BaseModel):
    """Beep sequence configuration (timing, repeats, optional frequency).

    Attributes:
        on_ms: On time in milliseconds (0-65535).
        off_ms: Off time in milliseconds (0-65535).
        repeats: Number of repeats (1-255).
        frequency: Optional frequency in Hz (100-20000, default 3136).
    """

    on_ms: int = Field(default=100, ge=0, le=65535, description="On time in ms")
    off_ms: int | None = Field(default=None, ge=0, le=65535, description="Off time in ms")
    repeats: int | None = Field(default=None, ge=1, le=255, description="Number of repeats")
    frequency: int | None = Field(
        default=None, ge=100, le=20000, description="Frequency in Hz (100-20000)"
    )

    def to_config_value(self) -> str:
        """Generate config value: on[,off[,repeats[,freq]]].

        The manufacturer documents omitting "the interval between beeps and
        number of repeats, for a single beep of the specified duration".
        """
        parts = [str(self.on_ms)]
        if self.off_ms is not None:
            parts.append(str(self.off_ms))
            if self.repeats is not None:
                parts.append(str(self.repeats))
                if self.frequency is not None:
                    parts.append(str(self.frequency))
        return ",".join(parts)


class LEDConfig(BaseModel):
    """LED configuration for VTAP100.

    Attributes:
        mode: LED operating mode.
        select: LED type/position.
        default_rgb: Default RGB color (6 hex chars).
        pass_led: LED sequence for pass read.
        tag_led: LED sequence for tag read.
        pass_error_led: LED sequence for pass error.
        start_led: LED sequence on startup.
    """

    mode: LEDMode | None = Field(default=None, description="LED mode")
    select: LEDSelect = Field(default=LEDSelect.ONBOARD_COMPACT, description="LED type/position")
    default_rgb: str | None = Field(default=None, description="Default RGB color")
    pass_led: LEDSequence | None = Field(default=None, description="Pass read LED")
    tag_led: LEDSequence | None = Field(default=None, description="Tag read LED")
    pass_error_led: LEDSequence | None = Field(default=None, description="Error LED")
    start_led: LEDSequence | None = Field(default=None, description="Startup LED")

    @field_validator("default_rgb")
    @classmethod
    def validate_default_rgb(cls, v: str | None) -> str | None:
        """Validate default_rgb is 6 hex characters."""
        if v is None:
            return None
        if len(v) != 6:
            msg = "Default RGB must be 6 hex characters"
            raise ValueError(msg)
        try:
            int(v, 16)
        except ValueError:
            msg = "Default RGB must be valid hex"
            raise ValueError(msg) from None
        return v.upper()

    def to_config_lines(self) -> list[str]:
        """Generate config.txt lines for LED settings.

        Returns:
            List of config.txt lines.
        """
        lines: list[str] = []

        if self.mode is not None:
            lines.append(f"LEDMode={self.mode.value}")

        # LEDSelect always has a default value
        lines.append(f"LEDSelect={self.select.value}")

        if self.default_rgb is not None:
            lines.append(f"LEDDefaultRGB={self.default_rgb}")

        if self.pass_led is not None:
            lines.append(f"PassLED={self.pass_led.to_config_value()}")

        if self.tag_led is not None:
            lines.append(f"TagLED={self.tag_led.to_config_value()}")

        if self.pass_error_led is not None:
            lines.append(f"PassErrorLED={self.pass_error_led.to_config_value()}")

        if self.start_led is not None:
            lines.append(f"StartLED={self.start_led.to_config_value()}")

        return lines


class BeepConfig(BaseModel):
    """Beep/Buzzer configuration for VTAP100.

    Attributes:
        pass_beep: Beep sequence for pass read.
        tag_beep: Beep sequence for tag read.
        pass_error_beep: Beep sequence for pass error.
        start_beep: Beep sequence on startup.
    """

    pass_beep: BeepSequence | None = Field(default=None, description="Pass read beep")
    tag_beep: BeepSequence | None = Field(default=None, description="Tag read beep")
    pass_error_beep: BeepSequence | None = Field(default=None, description="Error beep")
    start_beep: BeepSequence | None = Field(default=None, description="Startup beep")

    def to_config_lines(self) -> list[str]:
        """Generate config.txt lines for beep settings.

        Returns:
            List of config.txt lines.
        """
        lines: list[str] = []

        if self.pass_beep is not None:
            lines.append(f"PassBeep={self.pass_beep.to_config_value()}")

        if self.tag_beep is not None:
            lines.append(f"TagBeep={self.tag_beep.to_config_value()}")

        if self.pass_error_beep is not None:
            lines.append(f"PassErrorBeep={self.pass_error_beep.to_config_value()}")

        if self.start_beep is not None:
            lines.append(f"StartBeep={self.start_beep.to_config_value()}")

        return lines


class FeedbackConfig(BaseModel):
    """Combined LED and Beep configuration for VTAP100.

    Attributes:
        led: LED configuration.
        beep: Beep configuration.
    """

    led: LEDConfig | None = Field(default=None, description="LED configuration")
    beep: BeepConfig | None = Field(default=None, description="Beep configuration")

    def to_config_lines(self) -> list[str]:
        """Generate config.txt lines for all feedback settings.

        Returns:
            List of config.txt lines.
        """
        lines: list[str] = []

        if self.led is not None:
            lines.extend(self.led.to_config_lines())

        if self.beep is not None:
            lines.extend(self.beep.to_config_lines())

        return lines
