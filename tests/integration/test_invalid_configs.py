"""Rejection battery over the invalid fixture corpus.

Each file in tests/fixtures/invalid_configs/ must fail to parse, and the error
must name the field responsible — not merely be some error.
"""

from pathlib import Path
import pytest
from pydantic import ValidationError
from vtap100.parser import parse


FIXTURES = Path(__file__).parent.parent / "fixtures" / "invalid_configs"

# Fixture stem -> the model field the error must name.
EXPECTED_FIELD = {
    "desfire_fileid_256": "file_id",
    "desfire_keynum_16": "key_num",
    "desfire_keyslot_10": "key_slot",
    "vas_keyslot_7": "key_slot",
    "vas_merchant_id_no_prefix": "merchant_id",
}


def invalid_config_files() -> list[Path]:
    """Return every configuration expected to be rejected."""
    return sorted(FIXTURES.glob("*.txt"))


@pytest.mark.parametrize("config_path", invalid_config_files(), ids=lambda p: p.stem)
def test_is_rejected_naming_the_field(config_path: Path) -> None:
    """Parsing fails, and the error names the offending field."""
    expected = EXPECTED_FIELD[config_path.stem]
    with pytest.raises(ValidationError) as exc_info:
        parse(config_path.read_text())
    assert expected in str(exc_info.value), (
        f"error for {config_path.name} does not name {expected}: {exc_info.value}"
    )
