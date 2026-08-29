"""Pytest configuration and shared fixtures for VTAP100 tests."""

from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def reset_language():
    """Reset language to German (DE) before each test.

    This ensures tests don't affect each other through language state.
    """
    from vtap100.tui.i18n import Language
    from vtap100.tui.i18n import set_language

    set_language(Language.DE)
    yield
    # Reset again after test
    set_language(Language.DE)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_configs_dir(fixtures_dir: Path) -> Path:
    """Return path to valid config fixtures."""
    return fixtures_dir / "valid_configs"


@pytest.fixture
def invalid_configs_dir(fixtures_dir: Path) -> Path:
    """Return path to invalid config fixtures."""
    return fixtures_dir / "invalid_configs"


@pytest.fixture
def expected_outputs_dir(fixtures_dir: Path) -> Path:
    """Return path to expected output fixtures."""
    return fixtures_dir / "expected_outputs"


@pytest.fixture
def sample_apple_vas_config() -> dict:
    """Return a sample Apple VAS configuration dict."""
    return {
        "merchant_id": "pass.com.example.test",
        "key_slot": 1,
    }


@pytest.fixture
def sample_google_smarttap_config() -> dict:
    """Return a sample Google Smart Tap configuration dict."""
    return {
        "collector_id": "96972794",
        "key_slot": 2,
        "key_version": 1,
    }


@pytest.fixture
def sample_keyboard_config() -> dict:
    """Return a sample keyboard emulation configuration dict."""
    return {
        "log_mode": True,
        "source": "A1",
    }


@pytest.fixture
def local_configs_dir(fixtures_dir: Path) -> Path:
    """Return path to the git-ignored private config corpus."""
    return fixtures_dir / "local_configs"
