"""Apple Access (ECP2) configuration models.

Apple Access lets passes in Apple Wallet act as electronic keys. Setting
AccessTCI puts the reader in ECP2 mode and enables DESFire credential reading.

It does not disable Apple VAS. The manufacturer's wording reads like a mode
switch, but production configurations carry Apple VAS, Google Smart Tap and
Apple Access together in one file.

References:
    - https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Access-settings.htm
"""

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class AccessConfig(BaseModel):
    """Configuration for Access using Apple Wallet.

    Attributes:
        tci: Terminal Configuration Identifier, a hex value assigned by Apple to
            the credential issuer. Conventionally 3 bytes.
        auth_required: Require device authentication on every tap.
        ecp2_mode: 't' for Apple Transit, 'a' for Apple Access.
    """

    tci: str | None = Field(
        default=None,
        description="Terminal Configuration Identifier (hex, conventionally 3 bytes)",
    )
    auth_required: bool | None = Field(
        default=None,
        description="Require authentication on every tap (AccessAuthRequired)",
    )
    ecp2_mode: str | None = Field(
        default=None,
        pattern="^[ta]$",
        description="ECP2 mode: t=Apple Transit, a=Apple Access",
    )

    @field_validator("tci")
    @classmethod
    def validate_tci(cls, v: str | None) -> str | None:
        """Validate the TCI is hexadecimal of even length.

        The reader conventionally expects 3 bytes, but the exact length is not
        enforced so that valid TCIs of other lengths are not excluded. The byte
        semantics are the caller's responsibility.

        Args:
            v: The raw TCI value.

        Returns:
            The upper-cased TCI.

        Raises:
            ValueError: If the value is not even-length hexadecimal.
        """
        if v is None:
            return None
        candidate = v.strip().upper()
        if (
            not candidate
            or len(candidate) % 2
            or not all(char in "0123456789ABCDEF" for char in candidate)
        ):
            msg = "AccessTCI must be a hex string of even length"
            raise ValueError(msg)
        return candidate

    def to_config_lines(self) -> list[str]:
        """Generate config.txt lines for this Access configuration.

        Returns:
            List of config.txt lines for the fields that are set.
        """
        lines: list[str] = []
        if self.tci is not None:
            lines.append(f"AccessTCI={self.tci}")
        if self.auth_required is not None:
            lines.append(f"AccessAuthRequired={1 if self.auth_required else 0}")
        if self.ecp2_mode is not None:
            lines.append(f"ECP2Mode={self.ecp2_mode}")
        return lines
