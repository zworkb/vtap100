"""Serial port output configuration models.

The VTAP100 can emit read data over a serial port in addition to, or instead
of, keyboard emulation. ComPortSource carries the same bitmask as KBSource, so
KBSourceBuilder composes values for both rather than the bit meanings being
restated here.

References:
    - https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm
"""

from pydantic import BaseModel
from pydantic import Field


class ComPortConfig(BaseModel):
    """Configuration for serial port output.

    Attributes:
        enable: Whether serial output is enabled (ComPortEnable).
        mode: Serial output mode (ComPortMode).
        source: Which data sources trigger serial output (ComPortSource), as a
            hex bitmask. See KBSourceBuilder for the bit meanings.
    """

    enable: bool | None = Field(
        default=None,
        description="Enable serial port output (ComPortEnable)",
    )
    mode: int | None = Field(
        default=None,
        ge=0,
        description="Serial output mode (ComPortMode)",
    )
    source: str | None = Field(
        default=None,
        description="Data sources for serial output (ComPortSource, KBSource bitmask)",
    )

    def to_config_lines(self) -> list[str]:
        """Generate config.txt lines for this serial port configuration.

        Returns:
            List of config.txt lines for the fields that are set.
        """
        lines: list[str] = []
        if self.enable is not None:
            lines.append(f"ComPortEnable={1 if self.enable else 0}")
        if self.mode is not None:
            lines.append(f"ComPortMode={self.mode}")
        if self.source is not None:
            lines.append(f"ComPortSource={self.source}")
        return lines
