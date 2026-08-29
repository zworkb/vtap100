"""Google Smart Tap configuration models.

This module provides Pydantic models for configuring Google Wallet Smart Tap
on VTAP100 NFC readers. Smart Tap allows Google Wallet passes to be read
by NFC readers for loyalty, membership, and identity applications.

Example:
    >>> config = GoogleSmartTapConfig(
    ...     slot=2,
    ...     collector_id="96972794",
    ...     key_slot=1,
    ...     key_version=1,
    ... )
    >>> config.to_config_lines(slot_number=2)
    ['ST2CollectorID=96972794', 'ST2KeySlot=1', 'ST2KeyVersion=1']

Note:
    ST1 configuration does not work for Google Smart Tap. The generator
    automatically starts at ST2.

References:
    - https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-ST-settings.htm
    - https://www.passmeister.com/en/b/nfc_setup_dot_origin_vtap100_google_wallet
"""

from pydantic import BaseModel
from pydantic import Field
from vtap100.models.base import DefaultPassesEnabled


class GoogleSmartTapConfig(BaseModel):
    """Configuration for a single Google Smart Tap pass type.

    Attributes:
        slot: The pass slot number (1-6) appearing in the ST# parameter names.
        collector_id: The Google Collector ID (numeric string).
            Provided by Google to uniquely identify your passes.
        key_slot: The private key slot (1-6) where the decryption key is stored.
            Required for the reader to work correctly.
        key_version: The key version number that must match the Google dashboard.
            Defaults to 0 if not specified.
    """

    slot: int = Field(
        ...,
        ge=1,
        le=6,
        description="Pass slot number (1-6) used in the ST# parameter names",
    )
    collector_id: str = Field(
        ...,
        description="Google Collector ID (numeric string)",
        min_length=1,
    )
    key_slot: int | None = Field(
        default=None,
        ge=0,
        le=6,
        description="Private key slot (0-6; 0 or omitted is the documented default)",
    )
    key_version: int | None = Field(
        default=None,
        ge=0,
        description="Key version (must match Google dashboard)",
    )

    def to_config_lines(self, slot_number: int) -> list[str]:
        """Generate config.txt lines for this Smart Tap configuration.

        Args:
            slot_number: The ST slot number (2-6) to use in parameter names.
                Note: ST1 does not work, so the generator uses 2-6.

        Returns:
            List of config.txt lines (e.g., ['ST2CollectorID=...', 'ST2KeySlot=...']).
        """
        lines = [f"ST{slot_number}CollectorID={self.collector_id}"]

        if self.key_slot is not None:
            lines.append(f"ST{slot_number}KeySlot={self.key_slot}")

        if self.key_version is not None:
            lines.append(f"ST{slot_number}KeyVersion={self.key_version}")

        return lines


class STDefaultPassesEnabled(DefaultPassesEnabled):
    """Configuration for which Smart Tap pass slots are enabled at startup.

    This setting restricts which Smart Tap passes are checked at startup,
    reducing processing time when not all slots are in use.

    Note: Android supports only one Collector ID at a time.

    Attributes:
        enabled_passes: List of enabled pass numbers (1-6).
            Default is all passes enabled [1, 2, 3, 4, 5, 6].
    """

    CONFIG_PREFIX = "ST"
