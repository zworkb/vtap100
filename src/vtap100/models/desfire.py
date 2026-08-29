"""MIFARE DESFire configuration models for VTAP100 NFC reader.

This module provides models for configuring MIFARE DESFire card reading
on the VTAP100 NFC reader.

Phase 4 Implementation.
"""

from enum import IntEnum
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class DESFireCryptoMode(IntEnum):
    """DESFire cryptographic modes."""

    NONE = 0  # No encryption
    DES3 = 1  # 3DES encryption
    AES = 3  # AES encryption


class DESFireDataFormat(IntEnum):
    """DESFire data output formats."""

    RAW = 0  # Raw data
    KEYID_V1 = 1  # KEY-ID v1 format
    KEYID_V2 = 2  # KEY-ID v2 format


class DiversificationBuilder:
    """Builder for DESFire#Diversification bit field values.

    Mirrors KBSourceBuilder, the other bitmask setting in this codebase.

    - Bit 0 (0b001): AN10922 key diversification active
    - Bit 1 (0b010): omit the AID from the diversification input
    - Bit 2 (0b100): reverse UID byte order

    Choosing the wrong mode does not fail loudly: the reader computes a
    different diversified key and authentication simply stops working.

    Reference:
        https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-DESFire-settings.htm

    Example:
        >>> DiversificationBuilder().active().reverse_uid().build()
        5
    """

    ACTIVE = 0b001
    OMIT_AID = 0b010
    REVERSE_UID = 0b100

    def __init__(self) -> None:
        """Initialise an empty builder with value 0."""
        self._value: int = 0

    def active(self) -> "DiversificationBuilder":
        """Enable AN10922 key diversification."""
        self._value |= self.ACTIVE
        return self

    def omit_aid(self) -> "DiversificationBuilder":
        """Omit the AID from the diversification input."""
        self._value |= self.OMIT_AID
        return self

    def reverse_uid(self) -> "DiversificationBuilder":
        """Reverse UID byte order."""
        self._value |= self.REVERSE_UID
        return self

    def build(self) -> int:
        """Return the composed bit field value."""
        return self._value


class DESFireAppConfig(BaseModel):
    """Configuration for a single DESFire application.

    Attributes:
        app_id: Application ID (6 hex characters).
        file_id: File ID to read (0-255).
        key_num: Key number for authentication.
        key_slot: Key slot for authentication (1-9).
        crypto: Cryptographic mode.
        format: Data output format.
        read_length: Number of bytes to read (1-255, default 3).
        read_offset: Offset in file to start reading (0-255, default 0).
        diversification: Key diversification bit field (0, 1, 3, 5 or 7).
        privacy_key_num: Privacy key number.
        privacy_key_slot: Privacy key slot.
        sysid_key_slot: System ID key slot.
        sysid_length: System ID length (0-16).
    """

    app_id: str = Field(..., description="Application ID (6 hex characters)")
    file_id: int | None = Field(default=None, ge=0, le=255, description="File ID (0-255)")
    key_num: int | None = Field(default=None, ge=0, le=15, description="Key number (0-15)")
    key_slot: int | None = Field(default=None, ge=1, le=9, description="Key slot (1-9)")
    crypto: DESFireCryptoMode | None = Field(default=None, description="Crypto mode")
    format: DESFireDataFormat | None = Field(default=None, description="Data format")
    read_length: int | None = Field(
        default=None, ge=1, le=255, description="Read length (1-255, reader default 3)"
    )
    read_offset: int | None = Field(
        default=None, ge=0, le=255, description="Read offset (0-255, reader default 0)"
    )
    diversification: int | None = Field(
        default=None,
        ge=0,
        le=7,
        description="Key diversification bit field (0, 1, 3, 5 or 7)",
    )
    privacy_key_num: int | None = Field(
        default=None, ge=0, le=15, description="Privacy key number (0-15)"
    )
    privacy_key_slot: int | None = Field(
        default=None, ge=1, le=9, description="Privacy key slot (1-9)"
    )
    sysid_key_slot: int | None = Field(
        default=None, ge=0, le=9, description="System ID key slot (0-9)"
    )
    sysid_length: int | None = Field(
        default=None, ge=0, le=16, description="System ID length (0-16)"
    )

    @field_validator("diversification")
    @classmethod
    def validate_diversification(cls, v: int | None) -> int | None:
        """Reject modifier bits without the active bit.

        Bit 1 (omit AID) and bit 2 (reverse UID) modify how the AN10922 input is
        built. Setting either without bit 0 describes modifiers on a disabled
        feature, which the reader cannot act on.

        Args:
            v: The raw diversification value.

        Returns:
            The validated value.

        Raises:
            ValueError: If a modifier bit is set without bit 0.
        """
        if v is not None and v != 0 and not v & DiversificationBuilder.ACTIVE:
            msg = "diversification must be 0, or have bit 0 set (valid: 0, 1, 3, 5, 7)"
            raise ValueError(msg)
        return v

    @field_validator("app_id")
    @classmethod
    def validate_app_id(cls, v: str) -> str:
        """Validate app_id is 6 hex characters."""
        if len(v) != 6:
            msg = "App ID must be 6 hex characters"
            raise ValueError(msg)
        # Validate hex format
        try:
            int(v, 16)
        except ValueError:
            msg = "App ID must be valid hex"
            raise ValueError(msg) from None
        return v.upper()

    def to_config_lines(self, slot_number: int = 1) -> list[str]:
        """Generate config.txt lines for this DESFire app.

        Args:
            slot_number: The DESFire slot number (1-9).

        Returns:
            List of config.txt lines.
        """
        prefix = f"DESFire{slot_number}"
        lines: list[str] = []

        # App ID is always included
        lines.append(f"{prefix}AppID={self.app_id}")

        # Optional settings
        if self.file_id is not None:
            lines.append(f"{prefix}FileID={self.file_id}")

        if self.key_num is not None:
            lines.append(f"{prefix}KeyNum={self.key_num}")

        if self.key_slot is not None:
            lines.append(f"{prefix}KeySlot={self.key_slot}")

        if self.crypto is not None:
            lines.append(f"{prefix}Crypto={self.crypto.value}")

        if self.format is not None:
            lines.append(f"{prefix}Format={self.format.value}")

        # Read settings - only include if not default
        if self.read_length is not None:
            lines.append(f"{prefix}ReadLength={self.read_length}")

        if self.read_offset is not None:
            lines.append(f"{prefix}ReadOffset={self.read_offset}")

        if self.diversification is not None:
            lines.append(f"{prefix}Diversification={self.diversification}")

        if self.privacy_key_num is not None:
            lines.append(f"{prefix}PrivacyKeyNum={self.privacy_key_num}")

        if self.privacy_key_slot is not None:
            lines.append(f"{prefix}PrivacyKeySlot={self.privacy_key_slot}")

        if self.sysid_key_slot is not None:
            lines.append(f"{prefix}SysIDKeySlot={self.sysid_key_slot}")

        if self.sysid_length is not None:
            lines.append(f"{prefix}SysIDLength={self.sysid_length}")

        return lines


class DESFireConfig(BaseModel):
    """Configuration for multiple DESFire applications.

    Attributes:
        apps: List of DESFire application configurations (max 9).
        separator: Separator character for multiple apps (default ",").
    """

    apps: list[DESFireAppConfig] = Field(
        default_factory=list, description="DESFire applications (max 9)"
    )
    separator: str = Field(default=",", description="Separator for multiple apps")

    @field_validator("apps")
    @classmethod
    def validate_max_apps(cls, v: list[DESFireAppConfig]) -> list[DESFireAppConfig]:
        """Validate that there are at most 9 apps."""
        if len(v) > 9:
            msg = "Maximum 9 DESFire applications allowed"
            raise ValueError(msg)
        return v

    def to_config_lines(self) -> list[str]:
        """Generate config.txt lines for all DESFire apps.

        Returns:
            List of config.txt lines.
        """
        if not self.apps:
            return []

        lines: list[str] = []

        # Generate lines for each app with slot numbering
        for i, app in enumerate(self.apps, start=1):
            lines.extend(app.to_config_lines(slot_number=i))

        # Only include separator if not default
        if self.separator != ",":
            lines.append(f"DESFireSeparator={self.separator}")

        return lines
