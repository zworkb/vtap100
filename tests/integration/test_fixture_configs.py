"""Round-trip battery over the fixture corpus.

Every configuration in tests/fixtures/valid_configs/ must parse and survive a
load/save cycle unchanged. Files are discovered by glob, so adding a
configuration to the directory subjects it to the full battery with no change
to this file.
"""

from pathlib import Path
import pytest
from vtap100.generator import ConfigGenerator
from vtap100.parser import parse
from vtap100.roundtrip import compare


FIXTURES = Path(__file__).parent.parent / "fixtures"


def valid_config_files() -> list[Path]:
    """Return every configuration expected to parse and round-trip."""
    return sorted((FIXTURES / "valid_configs").glob("*.txt"))


def config_id(path: Path) -> str:
    """Readable test id for a fixture path."""
    return path.stem


@pytest.mark.parametrize("config_path", valid_config_files(), ids=config_id)
def test_parses_without_error(config_path: Path) -> None:
    """Every valid fixture loads."""
    config = parse(config_path.read_text())
    assert config is not None


@pytest.mark.parametrize("config_path", valid_config_files(), ids=config_id)
def test_roundtrip_preserves_all_settings(config_path: Path) -> None:
    """A load/save cycle loses and alters nothing."""
    report = compare(config_path.read_text())
    assert report.lost == [], f"lost settings: {report.lost}"
    assert report.changed == [], f"changed settings: {report.changed}"


@pytest.mark.parametrize("config_path", valid_config_files(), ids=config_id)
def test_roundtrip_is_idempotent(config_path: Path) -> None:
    """A second cycle changes nothing further."""
    once = ConfigGenerator(parse(config_path.read_text())).generate()
    twice = ConfigGenerator(parse(once)).generate()
    assert once == twice


@pytest.mark.parametrize("config_path", valid_config_files(), ids=config_id)
def test_model_equality_after_roundtrip(config_path: Path) -> None:
    """The model is unchanged by a cycle."""
    original = parse(config_path.read_text())
    regenerated = parse(ConfigGenerator(original).generate())
    assert regenerated == original
