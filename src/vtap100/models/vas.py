"""Apple VAS (Value Added Services) configuration models.

This module provides Pydantic models for configuring Apple Wallet VAS
on VTAP100 NFC readers. VAS allows Apple Wallet passes to be read
by NFC readers for loyalty, membership, and identity applications.

Example:
    >>> config = AppleVASConfig(
    ...     slot=1,
    ...     merchant_id="pass.com.example.myapp",
    ...     key_slot=1,
    ... )
    >>> config.to_config_lines(slot_number=1)
    ['VAS1MerchantID=pass.com.example.myapp', 'VAS1KeySlot=1']

References:
    - https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-VAS_settings.htm
    - https://www.passmeister.com/en/b/nfc_setup_dot_origin_vtap100_apple_wallet
"""

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from vtap100.models.base import DefaultPassesEnabled


class AppleVASConfig(BaseModel):
    """Configuration for a single Apple VAS pass type.

    Attributes:
        slot: The pass slot number (1-6) appearing in the VAS# parameter names.
        merchant_id: The Apple Pass Type ID (e.g., 'pass.com.company.passname').
            Must start with 'pass.' prefix.
        key_slot: The private key slot (0-6) where the decryption key is stored.
            Optional; 0 or omitted means the reader selects the key automatically.
        merchant_url: Optional URL to invoke when presenting a pass.
            Note: Currently unsupported by iOS for VAS-only transactions.
    """

    slot: int = Field(
        ...,
        ge=1,
        le=6,
        description="Pass slot number (1-6) used in the VAS# parameter names",
    )
    merchant_id: str = Field(
        ...,
        description="Apple Pass Type ID (must start with 'pass.')",
        min_length=1,
    )
    key_slot: int | None = Field(
        default=None,
        ge=0,
        le=6,
        description="Private key slot (0-6; 0 or omitted means automatic selection)",
    )
    merchant_url: str | None = Field(
        default=None,
        description="Optional URL for pass presentation",
    )

    @field_validator("merchant_id")
    @classmethod
    def validate_merchant_id(cls, v: str) -> str:
        """Validate that merchant_id starts with 'pass.' prefix.

        Args:
            v: The merchant_id value to validate.

        Returns:
            The validated merchant_id.

        Raises:
            ValueError: If merchant_id doesn't start with 'pass.'.
        """
        if not v.startswith("pass."):
            raise ValueError("merchant_id must start with 'pass.' prefix")
        return v

    def to_config_lines(self, slot_number: int) -> list[str]:
        """Generate config.txt lines for this VAS configuration.

        Args:
            slot_number: The VAS slot number (1-6) to use in parameter names.

        Returns:
            List of config.txt lines (e.g., ['VAS1MerchantID=...', 'VAS1KeySlot=...']).
        """
        lines = [f"VAS{slot_number}MerchantID={self.merchant_id}"]

        if self.key_slot is not None:
            lines.append(f"VAS{slot_number}KeySlot={self.key_slot}")

        if self.merchant_url:
            lines.append(f"VAS{slot_number}MerchantURL={self.merchant_url}")

        return lines


class VASDefaultPassesEnabled(DefaultPassesEnabled):
    """Configuration for which VAS pass slots are enabled at startup.

    This setting restricts which VAS passes are checked at startup,
    reducing processing time when not all slots are in use.

    Attributes:
        enabled_passes: List of enabled pass numbers (1-6).
            Default is all passes enabled [1, 2, 3, 4, 5, 6].
    """

    CONFIG_PREFIX = "VAS"
