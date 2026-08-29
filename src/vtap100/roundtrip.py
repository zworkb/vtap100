r"""Round-trip fidelity comparison for VTAP100 configuration files.

Defines what "lossless" means for this project: parsing a config.txt and
regenerating it must preserve every setting the file contains. Imported by both
the test battery and the CLI, so the tool and CI cannot disagree.

Example:
    >>> from vtap100.roundtrip import compare
    >>> report = compare("!VTAPconfig\\nVAS1MerchantID=pass.com.example.x\\nVAS1KeySlot=1\\n")
    >>> report.is_lossless
    True
"""

from dataclasses import dataclass
from dataclasses import field
from vtap100.generator import ConfigGenerator
from vtap100.parser import parse


# Values the manufacturer documents as equivalent spellings of one setting.
# NFCType#: "=U or =1", "=N or =2", "=B or =3".
NORMALISE: dict[str, dict[str, str]] = {
    "NFCType2": {"1": "U", "2": "N", "3": "B"},
    "NFCType4": {"1": "U", "2": "N", "3": "B"},
    "NFCType5": {"1": "U", "3": "B"},
}


# The un-numbered DESFire spelling is the single-read form of index 1. Unlike
# NORMALISE, which maps values, this maps the key itself: the generator always
# writes the numbered form back.
KEY_ALIASES: dict[str, str] = {
    "DESFireAppID": "DESFire1AppID",
    "DESFireFileID": "DESFire1FileID",
    "DESFireKeySlot": "DESFire1KeySlot",
    "DESFireKeyNum": "DESFire1KeyNum",
    "DESFireCrypto": "DESFire1Crypto",
    "DESFireFormat": "DESFire1Format",
    "DESFireReadLength": "DESFire1ReadLength",
    "DESFireReadOffset": "DESFire1ReadOffset",
    "DESFireKeyDiversification": "DESFire1Diversification",
    "DESFireDiversification": "DESFire1Diversification",
    "DESFirePrivacyKeyNum": "DESFire1PrivacyKeyNum",
    "DESFirePrivacyKeySlot": "DESFire1PrivacyKeySlot",
    "DESFireSysIDKeySlot": "DESFire1SysIDKeySlot",
    "DESFireSysIDLength": "DESFire1SysIDLength",
}


def extract_settings(text: str) -> dict[str, str]:
    """Extract the Key=Value settings from config.txt content.

    Comments, blank lines and the header are ignored, so generator-authored
    section comments and reordering do not count as differences.

    Args:
        text: Raw config.txt content.

    Returns:
        Mapping of setting name to raw value string.
    """
    settings: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(";") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        canonical = KEY_ALIASES.get(key.strip(), key.strip())
        settings[canonical] = value.strip()
    return settings


def normalise(key: str, value: str) -> str:
    """Map a value to its canonical spelling for comparison.

    Args:
        key: The setting name.
        value: The raw value.

    Returns:
        The canonical value, or the input unchanged when no alias applies.
    """
    return NORMALISE.get(key, {}).get(value, value)


@dataclass
class RoundTripReport:
    """Result of comparing a config against its regenerated form.

    Attributes:
        lost: Settings present in the input but absent from the output.
        changed: (key, input value, output value) for settings whose value
            differs after normalisation.
    """

    lost: list[str] = field(default_factory=list)
    changed: list[tuple[str, str, str]] = field(default_factory=list)

    @property
    def is_lossless(self) -> bool:
        """True when nothing was lost or altered."""
        return not self.lost and not self.changed


def compare(text: str) -> RoundTripReport:
    """Compare config content against the result of parsing and regenerating it.

    Args:
        text: Raw config.txt content.

    Returns:
        A report naming every setting a load/save cycle would lose or alter.
    """
    generated = ConfigGenerator(parse(text)).generate()
    original = extract_settings(text)
    result = extract_settings(generated)

    report = RoundTripReport()
    for key, value in original.items():
        if key not in result:
            report.lost.append(key)
        elif normalise(key, value) != normalise(key, result[key]):
            report.changed.append((key, value, result[key]))
    return report
