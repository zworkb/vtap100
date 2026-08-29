"""Keyboard emulation configuration models.

This module provides Pydantic models for configuring keyboard emulation
on VTAP100 NFC readers. Keyboard emulation sends pass data as keystrokes
to the connected computer, appearing as if typed on a keyboard.

Example:
    >>> config = KeyboardConfig(
    ...     log_mode=True,
    ...     source="A1",
    ... )
    >>> config.to_config_lines()
    ['KBLogMode=1', 'KBSource=A1']

References:
    - https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm
"""

from pydantic import BaseModel
from pydantic import Field


class KeyboardConfig(BaseModel):
    """Configuration for keyboard emulation.

    Keyboard emulation sends pass data as keystrokes to the host computer.
    When enabled, successful pass reads appear in any open text editor.

    Attributes:
        log_mode: Enable keyboard emulation (KBLogMode).
            True = send data as keystrokes, False = disabled.
        enable: Enable USB keyboard device function (KBEnable).
            Set False for Android integrations that don't need HID.
        source: Which data sources trigger keyboard output (KBSource).
            Hex string defining pass types (e.g., 'A1' for Apple VAS).
        prefix: Optional prefix before data (KBPrefix).
            Can be ASCII-hex (%0A) or variables ($t for timestamp).
        postfix: Suffix after data (KBPostfix). Default is newline (%0A).
        delay_ms: Delay between keystrokes in ms (KBDelayMS). Range: 5-255.
        pass_mode: Enable pass payload extraction (KBPassMode).
        pass_section: Which section to extract (KBPassSection).
        pass_separator: Separator character for sections (KBPassSeparator).
        pass_start: Start position for extraction (KBPassStart).
        pass_length: Length of extraction, 0 = all (KBPassLength).
    """

    log_mode: bool = Field(
        default=False,
        description="Enable keyboard emulation (KBLogMode)",
    )
    enable: bool | None = Field(
        default=None,
        description="Enable the USB keyboard device (KBEnable, reader default 1)",
    )
    source: str = Field(
        default="A5",
        description="Data sources for keyboard output (KBSource)",
    )
    prefix: str | None = Field(
        default=None,
        max_length=80,
        description="Keystrokes sent before the data (KBPrefix)",
    )
    postfix: str | None = Field(
        default=None,
        max_length=80,
        description="Keystrokes sent after the data (KBPostfix, reader default %0A)",
    )
    delay_ms: int | None = Field(
        default=None,
        ge=0,
        le=255,
        description=(
            "Inter-keystroke delay in ms (KBDelayMS). Parsing accepts 0-255; the "
            "manufacturer documents 5-255 and its own sample file uses 2."
        ),
    )
    pass_mode: bool | None = Field(
        default=None,
        description="Extract a delimited section (KBPassMode)",
    )
    pass_section: int | None = Field(
        default=None,
        ge=0,
        description="Section number to read (KBPassSection)",
    )
    pass_separator: str | None = Field(
        default=None,
        min_length=1,
        max_length=1,
        description="Section separator character (KBPassSeparator)",
    )
    pass_start: int | None = Field(
        default=None,
        ge=0,
        description="First character to read (KBPassStart)",
    )
    pass_length: int | None = Field(
        default=None,
        ge=0,
        description="Number of characters to read (KBPassLength)",
    )

    def to_config_lines(self) -> list[str]:
        """Generate config.txt lines for keyboard emulation settings.

        Returns:
            List of config.txt lines (e.g., ['KBLogMode=1', 'KBSource=A1']).
        """
        lines: list[str] = []

        lines.append(f"KBLogMode={1 if self.log_mode else 0}")

        if self.enable is not None:
            lines.append(f"KBEnable={1 if self.enable else 0}")

        if self.source != "A5" or self.log_mode:
            lines.append(f"KBSource={self.source}")

        if self.prefix is not None:
            lines.append(f"KBPrefix={self.prefix}")

        if self.postfix is not None:
            lines.append(f"KBPostfix={self.postfix}")

        if self.delay_ms is not None:
            lines.append(f"KBDelayMS={self.delay_ms}")

        if self.pass_mode is not None:
            lines.append(f"KBPassMode={1 if self.pass_mode else 0}")

        if self.pass_section is not None:
            lines.append(f"KBPassSection={self.pass_section}")

        if self.pass_separator is not None:
            lines.append(f"KBPassSeparator={self.pass_separator}")

        if self.pass_start is not None:
            lines.append(f"KBPassStart={self.pass_start}")

        if self.pass_length is not None:
            lines.append(f"KBPassLength={self.pass_length}")

        return lines


class KBSourceBuilder:
    """Builder for constructing KBSource hex bitmask values.

    KBSource uses hexadecimal bitmasks per official VTAP documentation:
    - Bit 7 (0x80): Mobile Pass (Apple VAS / Google Smart Tap)
    - Bit 6 (0x40): STUID
    - Bit 5 (0x20): Card Emulation Write Mode
    - Bit 2 (0x04): Scanners
    - Bit 1 (0x02): Command Interface Messages
    - Bit 0 (0x01): Card/Tag UID

    Reference:
        https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm

    Example:
        >>> source = KBSourceBuilder().mobile_pass().card_tag_uid().build()
        >>> source
        '81'

        >>> # Default A5 configuration
        >>> source = (KBSourceBuilder()
        ...     .mobile_pass()
        ...     .card_emulation()
        ...     .scanners()
        ...     .card_tag_uid()
        ...     .build())
        >>> source
        'A5'
    """

    # Bit masks for KBSource
    MOBILE_PASS = 0x80  # Bit 7: Apple VAS / Google Smart Tap
    STUID = 0x40  # Bit 6: STUID
    CARD_EMULATION = 0x20  # Bit 5: Card Emulation Write Mode
    SCANNERS = 0x04  # Bit 2: Scanners
    COMMAND_INTERFACE = 0x02  # Bit 1: Command Interface Messages
    CARD_TAG_UID = 0x01  # Bit 0: Card/Tag UID

    def __init__(self) -> None:
        """Initialize an empty KBSource builder with value 0."""
        self._value: int = 0

    def mobile_pass(self) -> "KBSourceBuilder":
        """Enable mobile pass data (Apple VAS / Google Smart Tap)."""
        self._value |= self.MOBILE_PASS
        return self

    def stuid(self) -> "KBSourceBuilder":
        """Enable STUID data."""
        self._value |= self.STUID
        return self

    def card_emulation(self) -> "KBSourceBuilder":
        """Enable card emulation write mode."""
        self._value |= self.CARD_EMULATION
        return self

    def scanners(self) -> "KBSourceBuilder":
        """Enable scanner input."""
        self._value |= self.SCANNERS
        return self

    def command_interface(self) -> "KBSourceBuilder":
        """Enable command interface messages."""
        self._value |= self.COMMAND_INTERFACE
        return self

    def card_tag_uid(self) -> "KBSourceBuilder":
        """Enable card/tag UID data."""
        self._value |= self.CARD_TAG_UID
        return self

    def build(self) -> str:
        """Build the final KBSource hex string.

        Returns:
            Uppercase hex string (e.g., "A5", "80", "01").
        """
        return f"{self._value:02X}"


def parse_kbsource_hex(hex_str: str) -> dict[str, bool]:
    """Parse a KBSource hex string into individual bit flags.

    Args:
        hex_str: Hex string like "A5", "80", "01"

    Returns:
        Dict with bit names as keys and bool values:
        {
            "mobile_pass": True/False,
            "stuid": True/False,
            "card_emulation": True/False,
            "scanners": True/False,
            "command_interface": True/False,
            "card_tag_uid": True/False,
        }

    Raises:
        ValueError: If hex_str is not a valid hex number

    Example:
        >>> parse_kbsource_hex("A5")
        {'mobile_pass': True, 'stuid': False, 'card_emulation': True,
         'scanners': True, 'command_interface': False, 'card_tag_uid': True}
    """
    value = int(hex_str, 16)
    return {
        "mobile_pass": bool(value & KBSourceBuilder.MOBILE_PASS),
        "stuid": bool(value & KBSourceBuilder.STUID),
        "card_emulation": bool(value & KBSourceBuilder.CARD_EMULATION),
        "scanners": bool(value & KBSourceBuilder.SCANNERS),
        "command_interface": bool(value & KBSourceBuilder.COMMAND_INTERFACE),
        "card_tag_uid": bool(value & KBSourceBuilder.CARD_TAG_UID),
    }


def build_kbsource_from_flags(
    mobile_pass: bool = False,
    stuid: bool = False,
    card_emulation: bool = False,
    scanners: bool = False,
    command_interface: bool = False,
    card_tag_uid: bool = False,
) -> str:
    """Build KBSource hex string from individual flags.

    Args:
        mobile_pass: Enable Mobile Pass (Apple VAS / Google Smart Tap)
        stuid: Enable STUID
        card_emulation: Enable Card Emulation Write Mode
        scanners: Enable Scanners
        command_interface: Enable Command Interface Messages
        card_tag_uid: Enable Card/Tag UID

    Returns:
        Uppercase hex string like "A5", "80", "01"

    Example:
        >>> build_kbsource_from_flags(mobile_pass=True, card_tag_uid=True)
        '81'
    """
    builder = KBSourceBuilder()
    if mobile_pass:
        builder.mobile_pass()
    if stuid:
        builder.stuid()
    if card_emulation:
        builder.card_emulation()
    if scanners:
        builder.scanners()
    if command_interface:
        builder.command_interface()
    if card_tag_uid:
        builder.card_tag_uid()
    return builder.build()
