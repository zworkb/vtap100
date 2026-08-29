"""Main VTAP100 configuration model.

This module provides the VTAPConfig model that combines all configuration
components into a single object for generating config.txt files.

Example:
    >>> from vtap100.models.config import VTAPConfig
    >>> from vtap100.models.vas import AppleVASConfig
    >>> from vtap100.models.keyboard import KeyboardConfig
    >>>
    >>> vas = AppleVASConfig(merchant_id="pass.com.example.test", key_slot=1)
    >>> kb = KeyboardConfig(log_mode=True, source="A1")
    >>> config = VTAPConfig(vas_configs=[vas], keyboard=kb)
"""

from pydantic import BaseModel
from pydantic import Field
from vtap100.models.access import AccessConfig
from vtap100.models.desfire import DESFireConfig
from vtap100.models.feedback import FeedbackConfig
from vtap100.models.keyboard import KeyboardConfig
from vtap100.models.nfc import NFCTagConfig
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.models.smarttap import STDefaultPassesEnabled
from vtap100.models.vas import AppleVASConfig
from vtap100.models.vas import VASDefaultPassesEnabled


class VTAPConfig(BaseModel):
    """Main configuration model for VTAP100 NFC reader.

    This model combines all configuration components:
    - Apple VAS configurations (up to 6)
    - Google Smart Tap configurations (up to 6)
    - Keyboard emulation settings
    - NFC tag settings
    - MIFARE DESFire settings
    - LED/Beep feedback settings

    Attributes:
        vas_configs: List of Apple VAS configurations (max 6).
        vas_default_passes: Optional VAS default passes enabled setting.
        smarttap_configs: List of Google Smart Tap configurations (max 6).
        smarttap_default_passes: Optional Smart Tap default passes enabled setting.
        keyboard: Keyboard emulation configuration.
        nfc: NFC tag reading configuration.
        desfire: MIFARE DESFire configuration.
        access: Apple Access (ECP2) configuration.
        feedback: LED and Beep feedback configuration.
    """

    vas_configs: list[AppleVASConfig] = Field(
        default_factory=list,
        max_length=6,
        description="Apple VAS configurations (max 6)",
    )
    vas_default_passes: VASDefaultPassesEnabled | None = Field(
        default=None,
        description="VAS default passes enabled setting",
    )
    smarttap_configs: list[GoogleSmartTapConfig] = Field(
        default_factory=list,
        max_length=6,
        description="Google Smart Tap configurations (max 6)",
    )
    smarttap_default_passes: STDefaultPassesEnabled | None = Field(
        default=None,
        description="Smart Tap default passes enabled setting",
    )
    keyboard: KeyboardConfig | None = Field(
        default=None,
        description="Keyboard emulation configuration",
    )
    nfc: NFCTagConfig | None = Field(
        default=None,
        description="NFC tag reading configuration",
    )
    desfire: DESFireConfig | None = Field(
        default=None,
        description="MIFARE DESFire configuration",
    )
    access: AccessConfig | None = Field(
        default=None,
        description="Apple Access (ECP2) configuration",
    )
    feedback: FeedbackConfig | None = Field(
        default=None,
        description="LED and Beep feedback configuration",
    )
