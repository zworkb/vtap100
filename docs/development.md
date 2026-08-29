# Development Guide

## Setup

```bash
git clone https://github.com/jensens/vtap100.git
cd vtap100
uv sync --extra dev
```

## Test-Driven Development (TDD)

This project follows strict TDD: **Write tests first, then implementation.**

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=vtap100 --cov-report=html

# Single file
uv run pytest tests/unit/test_models_vas.py -v
```

### TDD Cycle

1. **Red**: Write failing test
2. **Green**: Minimal implementation to pass
3. **Refactor**: Improve code, tests stay green

## Configuration Fixture Corpus

`tests/fixtures/` holds real configuration files that must survive a load/save
cycle unchanged. The battery in `tests/integration/test_fixture_configs.py` is
parametrised by glob, so **adding a configuration needs no test code**:

```
tests/fixtures/
├── valid_configs/     # must parse and round-trip losslessly
├── invalid_configs/   # must fail with a named field error
├── expected_outputs/  # canonical generator output
└── local_configs/     # git-ignored, your own un-anonymised files
```

Drop a file into `valid_configs/` and it is immediately subjected to four
checks: it parses, a cycle loses nothing, a second cycle changes nothing, and
the model compares equal afterwards.

### Contributing a configuration

Fixtures are public. Never commit real deployment identifiers or key material —
a leaked identifier stays in the git history after the file is corrected. A
pre-commit hook enforces this with an allowlist, so only placeholder values pass:

```bash
uv run pre-commit run fixture-leak-check --all-files
```

If you need a new placeholder value, extend the allowlist in
`scripts/check_fixture_leaks.py` deliberately — that edit is the moment to check
whether the value is genuinely an example.

### Testing against your own configurations

`tests/fixtures/local_configs/` is git-ignored. Files placed there are run
through the same battery and never leave your machine, which is the quickest way
to find out whether the tool handles a reader configuration you actually own.

## Code Quality

```bash
# Lint & format
uv run ruff check src tests
uv run ruff check --fix src tests
uv run ruff format src tests

# Type checking
uv run mypy src
```

## Project Structure

```
src/vtap100/
├── models/           # Pydantic models (vas, smarttap, keyboard, nfc, desfire, feedback)
├── generator.py      # config.txt generator
├── parser.py         # config.txt parser
├── cli.py            # CLI commands
└── tui/              # Terminal UI (Textual)
    ├── app.py        # Main app
    ├── screens/      # Editor, dialogs
    ├── widgets/      # Sidebar, forms, help panel, preview
    ├── i18n/         # Translations (de.yaml, en.yaml)
    └── help/         # Context-sensitive help (YAML)

tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── fixtures/         # Test data
```

## TUI Development

### i18n System

Translations in `tui/i18n/translations/{de,en}.yaml`:

```python
from vtap100.tui.i18n import t, set_language, Language

set_language(Language.DE)
label = t("common.buttons.save")  # "Speichern"
```

Language switch (Ctrl+L) preserves form values and tree expansion state.

## TUI Testing

Uses Textual's Pilot mode for async UI testing:

```python
@pytest.mark.asyncio
async def test_sidebar_navigation():
    app = VTAPEditorApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click("#vas-section")
        assert app.query_one("VASConfigForm") is not None
```

Coverage target: 85%+

## Docstrings

Google-style:

```python
def generate_config(config: VTAPConfig, output_path: Path) -> None:
    """Generate a VTAP100 config.txt file.

    Args:
        config: Configuration object.
        output_path: Output file path.

    Raises:
        ValidationError: If configuration is invalid.
    """
```

## Releases

Releases are managed via [GitHub Releases](https://github.com/jensens/vtap100/releases).
See [RELEASING.md](RELEASING.md) for the full process.

Version is derived from Git tags via `hatch-vcs`.

## Resources

- [VTAP Configuration Guide (PDF)](https://www.vtapnfc.com/downloads/VTAP_Configuration_Guide.pdf)
- [Reference Sources](references/sources.md)
