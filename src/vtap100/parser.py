"""config.txt file parser for VTAP100 NFC reader.

This module provides the ConfigParser class for parsing VTAP100
configuration files back into VTAPConfig objects.

Example:
    >>> from vtap100.parser import parse
    >>>
    >>> content = '''!VTAPconfig
    ... VAS1MerchantID=pass.com.example.test
    ... VAS1KeySlot=1
    ... '''
    >>> config = parse(content)
    >>> config.vas_configs[0].merchant_id
    'pass.com.example.test'
"""

from dataclasses import dataclass
from dataclasses import field
import re
from vtap100.models.config import VTAPConfig
from vtap100.models.desfire import DESFireAppConfig
from vtap100.models.desfire import DESFireConfig
from vtap100.models.desfire import DESFireCryptoMode
from vtap100.models.desfire import DESFireDataFormat
from vtap100.models.feedback import BeepConfig
from vtap100.models.feedback import BeepSequence
from vtap100.models.feedback import FeedbackConfig
from vtap100.models.feedback import LEDConfig
from vtap100.models.feedback import LEDMode
from vtap100.models.feedback import LEDSelect
from vtap100.models.feedback import LEDSequence
from vtap100.models.keyboard import KeyboardConfig
from vtap100.models.nfc import NFCTagConfig
from vtap100.models.nfc import NFCTagMode
from vtap100.models.nfc import TagKeyType
from vtap100.models.nfc import TagReadConfig
from vtap100.models.nfc import TagReadFormat
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.models.vas import AppleVASConfig


@dataclass
class _VASParseData:
    """Temporary data structure for parsing VAS configs."""

    merchant_id: str | None = None
    key_slot: int | None = None
    merchant_url: str | None = None


@dataclass
class _SmartTapParseData:
    """Temporary data structure for parsing Smart Tap configs."""

    collector_id: str | None = None
    key_slot: int | None = None
    key_version: int | None = None


@dataclass
class _KeyboardParseData:
    """Temporary data structure for parsing Keyboard config."""

    log_mode: bool | None = None
    source: str | None = None


@dataclass
class _NFCParseData:
    """Temporary data structure for parsing NFC config."""

    type2: str | None = None
    type4: str | None = None
    type5: str | None = None
    report_read_error: bool = False
    ignore_random_uid: bool = False
    byte_order_reversed: bool = False
    # TagRead settings
    tag_read_block_num: int | None = None
    tag_read_key_slot: int | None = None
    tag_read_key_type: str | None = None
    tag_read_offset: int = 0
    tag_read_length: int | None = None
    tag_read_format: str | None = None
    tag_read_min_digits: int | str | None = None


@dataclass
class _DESFireAppParseData:
    """Temporary data structure for parsing DESFire app config."""

    app_id: str | None = None
    file_id: int | None = None
    key_num: int | None = None
    key_slot: int | None = None
    crypto: int | None = None
    format: int | None = None
    read_length: int = 3
    read_offset: int = 0
    diversification: bool | None = None
    privacy_key_num: int | None = None
    privacy_key_slot: int | None = None
    sysid_key_slot: int | None = None
    sysid_length: int | None = None


@dataclass
class _DESFireParseData:
    """Temporary data structure for parsing DESFire config."""

    apps: dict[int, _DESFireAppParseData] = field(default_factory=dict)
    separator: str = ","


@dataclass
class _LEDParseData:
    """Temporary data structure for parsing LED config."""

    mode: int | None = None
    select: int | None = None
    default_rgb: str | None = None
    pass_led: str | None = None
    tag_led: str | None = None
    pass_error_led: str | None = None
    start_led: str | None = None


@dataclass
class _BeepParseData:
    """Temporary data structure for parsing Beep config."""

    pass_beep: str | None = None
    tag_beep: str | None = None
    pass_error_beep: str | None = None
    start_beep: str | None = None


class ConfigParser:
    """Parser for VTAP100 config.txt files.

    This class parses the config.txt content and creates a VTAPConfig object.

    Attributes:
        content: The raw config.txt content to parse.
    """

    HEADER = "!VTAPconfig"

    # Regex patterns for parsing
    # VAS patterns
    VAS_MERCHANT_ID = re.compile(r"^VAS(\d+)MerchantID=(.+)$")
    VAS_KEY_SLOT = re.compile(r"^VAS(\d+)KeySlot=(\d+)$")
    VAS_MERCHANT_URL = re.compile(r"^VAS(\d+)MerchantURL=(.+)$")

    # SmartTap patterns
    ST_COLLECTOR_ID = re.compile(r"^ST(\d+)CollectorID=(.+)$")
    ST_KEY_SLOT = re.compile(r"^ST(\d+)KeySlot=(\d+)$")
    ST_KEY_VERSION = re.compile(r"^ST(\d+)KeyVersion=(\d+)$")

    # Keyboard patterns
    KB_LOG_MODE = re.compile(r"^KBLogMode=(\d+)$")
    KB_SOURCE = re.compile(r"^KBSource=(.+)$")

    # NFC patterns
    NFC_TYPE2 = re.compile(r"^NFCType2=([0UNBDP])$")
    NFC_TYPE4 = re.compile(r"^NFCType4=([0UNBDP])$")
    NFC_TYPE5 = re.compile(r"^NFCType5=([0UNBDP])$")
    NFC_REPORT_READ_ERROR = re.compile(r"^NFCReportReadError=(\d+)$")
    IGNORE_RANDOM_UID = re.compile(r"^IgnoreRandomUID=(\d+)$")
    TAG_BYTE_ORDER = re.compile(r"^TagByteOrder=(\d+)$")
    TAG_READ_BLOCK_NUM = re.compile(r"^TagReadBlockNum=(\d+)$")
    TAG_READ_KEY_SLOT = re.compile(r"^TagReadKeySlot=(\d+)$")
    TAG_READ_KEY_TYPE = re.compile(r"^TagReadKeyType=([ABC])$")
    TAG_READ_OFFSET = re.compile(r"^TagReadOffset=(\d+)$")
    TAG_READ_LENGTH = re.compile(r"^TagReadLength=(\d+)$")
    TAG_READ_FORMAT = re.compile(r"^TagReadFormat=([adh])$")
    TAG_READ_MIN_DIGITS = re.compile(r"^TagReadMinDigits=(\d+|A)$")

    # DESFire patterns
    DESFIRE_APP_ID = re.compile(r"^DESFire(\d+)AppID=([A-Fa-f0-9]{6})$")
    DESFIRE_FILE_ID = re.compile(r"^DESFire(\d+)FileID=(\d+)$")
    DESFIRE_KEY_NUM = re.compile(r"^DESFire(\d+)KeyNum=(\d+)$")
    DESFIRE_KEY_SLOT = re.compile(r"^DESFire(\d+)KeySlot=(\d+)$")
    DESFIRE_CRYPTO = re.compile(r"^DESFire(\d+)Crypto=(\d+)$")
    DESFIRE_FORMAT = re.compile(r"^DESFire(\d+)Format=(\d+)$")
    DESFIRE_READ_LENGTH = re.compile(r"^DESFire(\d+)ReadLength=(\d+)$")
    DESFIRE_READ_OFFSET = re.compile(r"^DESFire(\d+)ReadOffset=(\d+)$")
    DESFIRE_DIVERSIFICATION = re.compile(r"^DESFire(\d+)Diversification=(\d+)$")
    DESFIRE_PRIVACY_KEY_NUM = re.compile(r"^DESFire(\d+)PrivacyKeyNum=(\d+)$")
    DESFIRE_PRIVACY_KEY_SLOT = re.compile(r"^DESFire(\d+)PrivacyKeySlot=(\d+)$")
    DESFIRE_SYSID_KEY_SLOT = re.compile(r"^DESFire(\d+)SysIDKeySlot=(\d+)$")
    DESFIRE_SYSID_LENGTH = re.compile(r"^DESFire(\d+)SysIDLength=(\d+)$")
    DESFIRE_SEPARATOR = re.compile(r"^DESFireSeparator=(.+)$")

    # LED patterns
    LED_MODE = re.compile(r"^LEDMode=(\d+)$")
    LED_SELECT = re.compile(r"^LEDSelect=(\d+)$")
    LED_DEFAULT_RGB = re.compile(r"^LEDDefaultRGB=([A-Fa-f0-9]{6})$")
    PASS_LED = re.compile(r"^PassLED=(.+)$")
    TAG_LED = re.compile(r"^TagLED=(.+)$")
    PASS_ERROR_LED = re.compile(r"^PassErrorLED=(.+)$")
    START_LED = re.compile(r"^StartLED=(.+)$")

    # Beep patterns
    PASS_BEEP = re.compile(r"^PassBeep=(.+)$")
    TAG_BEEP = re.compile(r"^TagBeep=(.+)$")
    PASS_ERROR_BEEP = re.compile(r"^PassErrorBeep=(.+)$")
    START_BEEP = re.compile(r"^StartBeep=(.+)$")

    def __init__(self, content: str) -> None:
        """Initialize the parser with config content.

        Args:
            content: The raw config.txt content to parse.
        """
        self.content = content
        self._vas_data: dict[int, _VASParseData] = {}
        self._smarttap_data: dict[int, _SmartTapParseData] = {}
        self._keyboard_data: _KeyboardParseData = _KeyboardParseData()
        self._nfc_data: _NFCParseData = _NFCParseData()
        self._desfire_data: _DESFireParseData = _DESFireParseData()
        self._led_data: _LEDParseData = _LEDParseData()
        self._beep_data: _BeepParseData = _BeepParseData()

    def parse(self) -> VTAPConfig:
        """Parse the config content into a VTAPConfig object.

        Returns:
            A VTAPConfig object with the parsed configuration.

        Raises:
            ValueError: If the config is missing the required header.
        """
        lines = self.content.strip().split("\n")

        if not lines or not lines[0].strip().startswith(self.HEADER):
            raise ValueError("Config must start with !VTAPconfig header")

        # Parse each line
        for line in lines[1:]:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith(";"):
                continue

            self._parse_line(line)

        return self._build_config()

    def _parse_line(self, line: str) -> None:
        """Parse a single config line.

        Args:
            line: A single line from the config file.
        """
        # VAS configurations
        if self._parse_vas_line(line):
            return

        # Smart Tap configurations
        if self._parse_smarttap_line(line):
            return

        # Keyboard configuration
        if self._parse_keyboard_line(line):
            return

        # NFC configuration
        if self._parse_nfc_line(line):
            return

        # DESFire configuration
        if self._parse_desfire_line(line):
            return

        # LED configuration
        if self._parse_led_line(line):
            return

        # Beep configuration
        if self._parse_beep_line(line):
            return

    def _parse_vas_line(self, line: str) -> bool:
        """Parse VAS-related config line."""
        if match := self.VAS_MERCHANT_ID.match(line):
            slot = int(match.group(1))
            self._get_vas_data(slot).merchant_id = match.group(2)
            return True

        if match := self.VAS_KEY_SLOT.match(line):
            slot = int(match.group(1))
            self._get_vas_data(slot).key_slot = int(match.group(2))
            return True

        if match := self.VAS_MERCHANT_URL.match(line):
            slot = int(match.group(1))
            self._get_vas_data(slot).merchant_url = match.group(2)
            return True

        return False

    def _parse_smarttap_line(self, line: str) -> bool:
        """Parse SmartTap-related config line."""
        if match := self.ST_COLLECTOR_ID.match(line):
            slot = int(match.group(1))
            self._get_smarttap_data(slot).collector_id = match.group(2)
            return True

        if match := self.ST_KEY_SLOT.match(line):
            slot = int(match.group(1))
            self._get_smarttap_data(slot).key_slot = int(match.group(2))
            return True

        if match := self.ST_KEY_VERSION.match(line):
            slot = int(match.group(1))
            self._get_smarttap_data(slot).key_version = int(match.group(2))
            return True

        return False

    def _parse_keyboard_line(self, line: str) -> bool:
        """Parse Keyboard-related config line."""
        if match := self.KB_LOG_MODE.match(line):
            self._keyboard_data.log_mode = match.group(1) == "1"
            return True

        if match := self.KB_SOURCE.match(line):
            self._keyboard_data.source = match.group(1)
            return True

        return False

    def _parse_nfc_line(self, line: str) -> bool:
        """Parse NFC-related config line."""
        if match := self.NFC_TYPE2.match(line):
            self._nfc_data.type2 = match.group(1)
            return True

        if match := self.NFC_TYPE4.match(line):
            self._nfc_data.type4 = match.group(1)
            return True

        if match := self.NFC_TYPE5.match(line):
            self._nfc_data.type5 = match.group(1)
            return True

        if match := self.NFC_REPORT_READ_ERROR.match(line):
            self._nfc_data.report_read_error = match.group(1) == "1"
            return True

        if match := self.IGNORE_RANDOM_UID.match(line):
            self._nfc_data.ignore_random_uid = match.group(1) == "1"
            return True

        if match := self.TAG_BYTE_ORDER.match(line):
            self._nfc_data.byte_order_reversed = match.group(1) == "1"
            return True

        if match := self.TAG_READ_BLOCK_NUM.match(line):
            self._nfc_data.tag_read_block_num = int(match.group(1))
            return True

        if match := self.TAG_READ_KEY_SLOT.match(line):
            self._nfc_data.tag_read_key_slot = int(match.group(1))
            return True

        if match := self.TAG_READ_KEY_TYPE.match(line):
            self._nfc_data.tag_read_key_type = match.group(1)
            return True

        if match := self.TAG_READ_OFFSET.match(line):
            self._nfc_data.tag_read_offset = int(match.group(1))
            return True

        if match := self.TAG_READ_LENGTH.match(line):
            self._nfc_data.tag_read_length = int(match.group(1))
            return True

        if match := self.TAG_READ_FORMAT.match(line):
            self._nfc_data.tag_read_format = match.group(1)
            return True

        if match := self.TAG_READ_MIN_DIGITS.match(line):
            value = match.group(1)
            self._nfc_data.tag_read_min_digits = value if value == "A" else int(value)
            return True

        return False

    def _parse_desfire_line(self, line: str) -> bool:
        """Parse DESFire-related config line."""
        if match := self.DESFIRE_APP_ID.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).app_id = match.group(2).upper()
            return True

        if match := self.DESFIRE_FILE_ID.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).file_id = int(match.group(2))
            return True

        if match := self.DESFIRE_KEY_NUM.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).key_num = int(match.group(2))
            return True

        if match := self.DESFIRE_KEY_SLOT.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).key_slot = int(match.group(2))
            return True

        if match := self.DESFIRE_CRYPTO.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).crypto = int(match.group(2))
            return True

        if match := self.DESFIRE_FORMAT.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).format = int(match.group(2))
            return True

        if match := self.DESFIRE_READ_LENGTH.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).read_length = int(match.group(2))
            return True

        if match := self.DESFIRE_READ_OFFSET.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).read_offset = int(match.group(2))
            return True

        if match := self.DESFIRE_DIVERSIFICATION.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).diversification = match.group(2) == "1"
            return True

        if match := self.DESFIRE_PRIVACY_KEY_NUM.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).privacy_key_num = int(match.group(2))
            return True

        if match := self.DESFIRE_PRIVACY_KEY_SLOT.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).privacy_key_slot = int(match.group(2))
            return True

        if match := self.DESFIRE_SYSID_KEY_SLOT.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).sysid_key_slot = int(match.group(2))
            return True

        if match := self.DESFIRE_SYSID_LENGTH.match(line):
            slot = int(match.group(1))
            self._get_desfire_app_data(slot).sysid_length = int(match.group(2))
            return True

        if match := self.DESFIRE_SEPARATOR.match(line):
            self._desfire_data.separator = match.group(1)
            return True

        return False

    def _parse_led_line(self, line: str) -> bool:
        """Parse LED-related config line."""
        if match := self.LED_MODE.match(line):
            self._led_data.mode = int(match.group(1))
            return True

        if match := self.LED_SELECT.match(line):
            self._led_data.select = int(match.group(1))
            return True

        if match := self.LED_DEFAULT_RGB.match(line):
            self._led_data.default_rgb = match.group(1).upper()
            return True

        if match := self.PASS_LED.match(line):
            self._led_data.pass_led = match.group(1)
            return True

        if match := self.TAG_LED.match(line):
            self._led_data.tag_led = match.group(1)
            return True

        if match := self.PASS_ERROR_LED.match(line):
            self._led_data.pass_error_led = match.group(1)
            return True

        if match := self.START_LED.match(line):
            self._led_data.start_led = match.group(1)
            return True

        return False

    def _parse_beep_line(self, line: str) -> bool:
        """Parse Beep-related config line."""
        if match := self.PASS_BEEP.match(line):
            self._beep_data.pass_beep = match.group(1)
            return True

        if match := self.TAG_BEEP.match(line):
            self._beep_data.tag_beep = match.group(1)
            return True

        if match := self.PASS_ERROR_BEEP.match(line):
            self._beep_data.pass_error_beep = match.group(1)
            return True

        if match := self.START_BEEP.match(line):
            self._beep_data.start_beep = match.group(1)
            return True

        return False

    def _get_vas_data(self, slot: int) -> _VASParseData:
        """Get or create VAS data for a slot."""
        if slot not in self._vas_data:
            self._vas_data[slot] = _VASParseData()
        return self._vas_data[slot]

    def _get_smarttap_data(self, slot: int) -> _SmartTapParseData:
        """Get or create Smart Tap data for a slot."""
        if slot not in self._smarttap_data:
            self._smarttap_data[slot] = _SmartTapParseData()
        return self._smarttap_data[slot]

    def _get_desfire_app_data(self, slot: int) -> _DESFireAppParseData:
        """Get or create DESFire app data for a slot."""
        if slot not in self._desfire_data.apps:
            self._desfire_data.apps[slot] = _DESFireAppParseData()
        return self._desfire_data.apps[slot]

    def _build_config(self) -> VTAPConfig:
        """Build the final VTAPConfig from parsed data."""
        vas_configs: list[AppleVASConfig] = []
        smarttap_configs: list[GoogleSmartTapConfig] = []
        keyboard: KeyboardConfig | None = None
        nfc: NFCTagConfig | None = None
        desfire: DESFireConfig | None = None
        feedback: FeedbackConfig | None = None

        # Build VAS configs in order
        for slot in sorted(self._vas_data.keys()):
            data = self._vas_data[slot]
            if data.merchant_id:
                vas_configs.append(
                    AppleVASConfig(
                        merchant_id=data.merchant_id,
                        key_slot=data.key_slot,
                        merchant_url=data.merchant_url,
                    )
                )

        # Build Smart Tap configs in order
        for slot in sorted(self._smarttap_data.keys()):
            data = self._smarttap_data[slot]
            if data.collector_id:
                smarttap_configs.append(
                    GoogleSmartTapConfig(
                        collector_id=data.collector_id,
                        key_slot=data.key_slot,
                        key_version=data.key_version,
                    )
                )

        # Build Keyboard config
        if self._keyboard_data.log_mode is not None or self._keyboard_data.source is not None:
            keyboard = KeyboardConfig(
                log_mode=self._keyboard_data.log_mode or False,
                source=self._keyboard_data.source or "A5",
            )

        # Build NFC config
        nfc = self._build_nfc_config()

        # Build DESFire config
        desfire = self._build_desfire_config()

        # Build Feedback config
        feedback = self._build_feedback_config()

        return VTAPConfig(
            vas_configs=vas_configs,
            smarttap_configs=smarttap_configs,
            keyboard=keyboard,
            nfc=nfc,
            desfire=desfire,
            feedback=feedback,
        )

    def _build_nfc_config(self) -> NFCTagConfig | None:
        """Build NFC config from parsed data."""
        data = self._nfc_data

        # Check if any NFC data was parsed
        has_nfc_data = any(
            [
                data.type2,
                data.type4,
                data.type5,
                data.report_read_error,
                data.ignore_random_uid,
                data.byte_order_reversed,
                data.tag_read_block_num is not None,
                data.tag_read_key_slot is not None,
                data.tag_read_key_type is not None,
                data.tag_read_length is not None,
                data.tag_read_format is not None,
                data.tag_read_min_digits is not None,
            ]
        )

        if not has_nfc_data:
            return None

        # Build TagReadConfig if needed
        tag_read: TagReadConfig | None = None
        has_tag_read = any(
            [
                data.tag_read_block_num is not None,
                data.tag_read_key_slot is not None,
                data.tag_read_key_type is not None,
                data.tag_read_length is not None,
                data.tag_read_format is not None,
                data.tag_read_min_digits is not None,
            ]
        )

        if has_tag_read:
            tag_read = TagReadConfig(
                block_num=data.tag_read_block_num,
                key_slot=data.tag_read_key_slot,
                key_type=TagKeyType(data.tag_read_key_type) if data.tag_read_key_type else None,
                offset=data.tag_read_offset,
                length=data.tag_read_length,
                format=TagReadFormat(data.tag_read_format) if data.tag_read_format else None,
                min_digits=data.tag_read_min_digits,
            )

        return NFCTagConfig(
            type2=NFCTagMode(data.type2) if data.type2 else None,
            type4=NFCTagMode(data.type4) if data.type4 else None,
            type5=NFCTagMode(data.type5) if data.type5 else None,
            report_read_error=data.report_read_error,
            ignore_random_uid=data.ignore_random_uid,
            byte_order_reversed=data.byte_order_reversed,
            tag_read=tag_read,
        )

    def _build_desfire_config(self) -> DESFireConfig | None:
        """Build DESFire config from parsed data."""
        if not self._desfire_data.apps:
            return None

        apps: list[DESFireAppConfig] = []
        for slot in sorted(self._desfire_data.apps.keys()):
            data = self._desfire_data.apps[slot]
            if data.app_id:
                apps.append(
                    DESFireAppConfig(
                        app_id=data.app_id,
                        file_id=data.file_id,
                        key_num=data.key_num,
                        key_slot=data.key_slot,
                        crypto=DESFireCryptoMode(data.crypto) if data.crypto is not None else None,
                        format=DESFireDataFormat(data.format) if data.format is not None else None,
                        read_length=data.read_length,
                        read_offset=data.read_offset,
                        diversification=data.diversification,
                        privacy_key_num=data.privacy_key_num,
                        privacy_key_slot=data.privacy_key_slot,
                        sysid_key_slot=data.sysid_key_slot,
                        sysid_length=data.sysid_length,
                    )
                )

        if not apps:
            return None

        return DESFireConfig(
            apps=apps,
            separator=self._desfire_data.separator,
        )

    def _build_feedback_config(self) -> FeedbackConfig | None:
        """Build Feedback config from parsed data."""
        led_config = self._build_led_config()
        beep_config = self._build_beep_config()

        if led_config is None and beep_config is None:
            return None

        return FeedbackConfig(led=led_config, beep=beep_config)

    def _build_led_config(self) -> LEDConfig | None:
        """Build LED config from parsed data."""
        data = self._led_data

        has_led_data = any(
            [
                data.mode is not None,
                data.select is not None,
                data.default_rgb is not None,
                data.pass_led is not None,
                data.tag_led is not None,
                data.pass_error_led is not None,
                data.start_led is not None,
            ]
        )

        if not has_led_data:
            return None

        return LEDConfig(
            mode=LEDMode(data.mode) if data.mode is not None else None,
            select=LEDSelect(data.select) if data.select is not None else LEDSelect.ONBOARD_COMPACT,
            default_rgb=data.default_rgb,
            pass_led=self._parse_led_sequence(data.pass_led),
            tag_led=self._parse_led_sequence(data.tag_led),
            pass_error_led=self._parse_led_sequence(data.pass_error_led),
            start_led=self._parse_led_sequence(data.start_led),
        )

    def _build_beep_config(self) -> BeepConfig | None:
        """Build Beep config from parsed data."""
        data = self._beep_data

        has_beep_data = any(
            [
                data.pass_beep is not None,
                data.tag_beep is not None,
                data.pass_error_beep is not None,
                data.start_beep is not None,
            ]
        )

        if not has_beep_data:
            return None

        return BeepConfig(
            pass_beep=self._parse_beep_sequence(data.pass_beep),
            tag_beep=self._parse_beep_sequence(data.tag_beep),
            pass_error_beep=self._parse_beep_sequence(data.pass_error_beep),
            start_beep=self._parse_beep_sequence(data.start_beep),
        )

    def _parse_led_sequence(self, value: str | None) -> LEDSequence | None:
        """Parse LED sequence from config value.

        Format: color,on_ms,off_ms,repeats
        Example: 00FF00,100,50,3
        """
        if value is None:
            return None

        parts = value.split(",")
        if len(parts) != 4:
            return None

        return LEDSequence(
            color=parts[0].upper(),
            on_ms=int(parts[1]),
            off_ms=int(parts[2]),
            repeats=int(parts[3]),
        )

    def _parse_beep_sequence(self, value: str | None) -> BeepSequence | None:
        """Parse Beep sequence from config value.

        Format: on_ms,off_ms,repeats[,frequency]
        Example: 100,50,2 or 100,50,2,2000
        """
        if value is None:
            return None

        parts = value.split(",")
        if len(parts) < 3:
            return None

        frequency = int(parts[3]) if len(parts) >= 4 else None

        return BeepSequence(
            on_ms=int(parts[0]),
            off_ms=int(parts[1]),
            repeats=int(parts[2]),
            frequency=frequency,
        )


def parse(content: str) -> VTAPConfig:
    """Parse config.txt content into a VTAPConfig object.

    This is a convenience function that creates a ConfigParser and parses the content.

    Args:
        content: The raw config.txt content to parse.

    Returns:
        A VTAPConfig object with the parsed configuration.

    Raises:
        ValueError: If the config is missing the required header.

    Example:
        >>> content = '''!VTAPconfig
        ... VAS1MerchantID=pass.com.example.test
        ... VAS1KeySlot=1
        ... '''
        >>> config = parse(content)
        >>> config.vas_configs[0].merchant_id
        'pass.com.example.test'
    """
    parser = ConfigParser(content)
    return parser.parse()
