# Lossless config.txt Round-Trip — Implementation Plan (Part 1: Core)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every real VTAP100 `config.txt` — including the manufacturer's own published example — survive a load/save cycle without losing or altering a single setting.

**Architecture:** A comparison module (`roundtrip.py`) defines what "lossless" means and is imported by both the tests and, later, the CLI. A fixture corpus under `tests/fixtures/` is parametrised by glob so new configurations join the battery without touching test code. Each defect from the spec is then fixed in its own task: constraint corrections in the Pydantic models, missing settings wired into the parser, and slot numbers carried through the models instead of being re-derived from list position.

**Tech Stack:** Python 3.11+, Pydantic v2, pytest (+pytest-asyncio), Textual, click, uv, ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-08-28-config-roundtrip-design.md`

## Global Constraints

- **TDD is mandatory.** Every task writes the failing test first, observes it fail, then implements. This is the project's first directive in `CLAUDE.md`.
- **Commit after every task.** Project rule. Do not push — the user pushes.
- **Manufacturer specification wins** over the repository's own documentation. Every range is quoted in section 9 of the spec.
- **Tolerant read, strict create:** parsing accepts the full technically valid range and preserves values verbatim; TUI/CLI input constrains to the documented range. `KBDelayMS` is the only known divergence: model `ge=0, le=255`, TUI input `min=5, max=255`.
- **UI strings are bilingual.** Any new label needs an entry in both `src/vtap100/tui/i18n/translations/de.yaml` and `en.yaml`. Help texts go in `src/vtap100/tui/help/de/*.yaml` and `en/*.yaml`.
- **English only** in code, comments, docstrings and documentation.
- **No empty `__init__.py`.** Do not create one unless packaging demands it.
- **Coverage floor is 93%** (`pyproject.toml`, `fail_under = 93`). Current value is 95.13% — do not regress below the floor.
- **Verification command set:** `uv run --extra dev pytest -q`, `uv run --extra dev ruff check .`, `uv run --extra dev ruff format --check .`, `uv run --extra dev mypy src/`.
- **Never commit key material.** `.pem`, `.key` and `appkey*.txt` files must not enter the repository.

---

## File Structure

**Created:**

| Path | Responsibility |
|---|---|
| `src/vtap100/roundtrip.py` | The single definition of "lossless": extract settings, compare, report. Imported by tests now and by the CLI in Part 2. |
| `src/vtap100/models/access.py` | `AccessConfig` — Apple Access (`AccessTCI`, `AccessAuthRequired`, `ECP2Mode`). |
| `src/vtap100/models/comport.py` | `ComPortConfig` — serial output (`ComPortEnable`, `ComPortMode`, `ComPortSource`). |
| `tests/fixtures/valid_configs/*.txt` | Configurations that must parse and round-trip losslessly. |
| `tests/fixtures/invalid_configs/*.txt` | Configurations that must fail with a named field error. |
| `tests/integration/test_fixture_configs.py` | The round-trip battery, parametrised by glob. |
| `tests/integration/test_invalid_configs.py` | Rejection battery, parametrised by glob. |
| `tests/unit/test_roundtrip.py` | Unit tests for the comparison module itself. |

**Modified:**

| Path | Change |
|---|---|
| `src/vtap100/models/vas.py` | `slot` added; `key_slot` becomes optional `0..6`. |
| `src/vtap100/models/smarttap.py` | Same as VAS. |
| `src/vtap100/models/desfire.py` | `file_id` `ge=0`; `key_num`, `sysid_key_slot`, `privacy_key_slot` ranges; `diversification` becomes `int`; `read_length`/`read_offset` become optional. `DiversificationBuilder` added. |
| `src/vtap100/models/keyboard.py` | Eight fields become optional so "explicitly set" is distinguishable from "defaulted". |
| `src/vtap100/models/feedback.py` | `LEDSequence`/`BeepSequence` trailing fields become optional. |
| `src/vtap100/models/config.py` | `access` and `com_port` wired into `VTAPConfig`. |
| `src/vtap100/parser.py` | Slot preservation; nine keyboard regexes; short forms; NFCType aliases; un-numbered DESFire; Access; ComPort. |
| `src/vtap100/generator.py` | Emit `config.slot` instead of `enumerate`; emit newly supported settings; Jinja template key-slot fix. |
| `src/vtap100/tui/widgets/forms/desfire.py` | `Switch` → three checkboxes for the diversification bit field. |
| `tests/conftest.py` | Fixture-path helpers wired to the now-existing directories. |
| `.gitignore` | `*.pem`, `*.key`, `appkey*.txt`. |

---

## Task 1: Round-trip comparison module

The definition of "lossless" lives in one place. Tests and, later, the CLI both import it, so the tool and CI can never disagree about what the word means.

**Files:**
- Create: `src/vtap100/roundtrip.py`
- Test: `tests/unit/test_roundtrip.py`

**Interfaces:**
- Consumes: `vtap100.parser.parse`, `vtap100.generator.ConfigGenerator`
- Produces:
  - `extract_settings(text: str) -> dict[str, str]`
  - `NORMALISE: dict[str, dict[str, str]]`
  - `RoundTripReport` with `.lost: list[str]`, `.changed: list[tuple[str, str, str]]`, `.is_lossless: bool`
  - `compare(text: str) -> RoundTripReport`

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_roundtrip.py`:

```python
"""Unit tests for the round-trip comparison module."""

import pytest


class TestExtractSettings:
    """Tests for extracting Key=Value pairs from config text."""

    def test_extracts_key_value_pairs(self) -> None:
        """Plain settings become a dict."""
        from vtap100.roundtrip import extract_settings

        result = extract_settings("!VTAPconfig\nVAS1KeySlot=2\nKBSource=81\n")
        assert result == {"VAS1KeySlot": "2", "KBSource": "81"}

    def test_ignores_comments_and_blank_lines(self) -> None:
        """Comment lines and blanks are not settings."""
        from vtap100.roundtrip import extract_settings

        text = "!VTAPconfig\n\n; a comment\n;KBPassStart=0\nKBSource=81\n"
        assert extract_settings(text) == {"KBSource": "81"}

    def test_keeps_value_containing_equals(self) -> None:
        """Only the first '=' separates key from value."""
        from vtap100.roundtrip import extract_settings

        result = extract_settings("VAS1MerchantURL=https://x.example/?a=b\n")
        assert result == {"VAS1MerchantURL": "https://x.example/?a=b"}


class TestNormalisation:
    """Tests for documented-alias normalisation."""

    def test_nfctype_numeric_alias_equals_letter(self) -> None:
        """NFCType4=1 and NFCType4=U are the same setting."""
        from vtap100.roundtrip import normalise

        assert normalise("NFCType4", "1") == normalise("NFCType4", "U")

    def test_unrelated_setting_is_compared_verbatim(self) -> None:
        """Normalisation applies only to documented aliases."""
        from vtap100.roundtrip import normalise

        assert normalise("KBSource", "81") == "81"
        assert normalise("KBSource", "1") != normalise("KBSource", "U")


class TestCompare:
    """Tests for the round-trip report."""

    def test_lossless_config_reports_no_loss(self) -> None:
        """A config the tool fully supports round-trips cleanly."""
        from vtap100.roundtrip import compare

        report = compare("!VTAPconfig\nVAS1MerchantID=pass.com.example.x\nVAS1KeySlot=1\n")
        assert report.is_lossless
        assert report.lost == []
        assert report.changed == []

    def test_reports_lost_setting(self) -> None:
        """A setting the tool does not support is reported as lost.

        BTEnable is a Bluetooth setting and an explicit non-goal (spec section
        4), so it stays unsupported and this test stays valid. Do not use a
        setting that a later task adds support for.
        """
        from vtap100.roundtrip import compare

        report = compare(
            "!VTAPconfig\nVAS1MerchantID=pass.com.example.x\nVAS1KeySlot=1\nBTEnable=1\n"
        )
        assert "BTEnable" in report.lost
        assert not report.is_lossless
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run --extra dev pytest tests/unit/test_roundtrip.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'vtap100.roundtrip'`

- [ ] **Step 3: Write the implementation**

Create `src/vtap100/roundtrip.py`. Note the `r"""` — the docstring example
contains backslashes and ruff's D301 rule requires a raw string:

```python
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
        settings[key.strip()] = value.strip()
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run --extra dev pytest tests/unit/test_roundtrip.py -q`
Expected: PASS, 6 tests.

- [ ] **Step 5: Check quality gates**

Run: `uv run --extra dev ruff check . && uv run --extra dev ruff format --check . && uv run --extra dev mypy src/`
Expected: all clean.

- [ ] **Step 6: Commit**

```bash
git add src/vtap100/roundtrip.py tests/unit/test_roundtrip.py
git commit -m "feat: add round-trip comparison module

Defines lossless as: every Key=Value in the input reappears with an
equal value after parse and regenerate, comparing through a table of
documented aliases so NFCType4=1 and NFCType4=U count as equal.

One implementation, imported by tests and later the CLI, so the tool
and CI cannot disagree about what lossless means."
```

---

## Task 2: Fixture corpus scaffolding and the round-trip battery

The battery must exist before the fixes so each later task can add its fixture and watch it go green. It starts with a configuration the tool already handles, so the suite is green at the end of this task.

**Files:**
- Create: `tests/fixtures/valid_configs/vas_basic.txt`, `tests/fixtures/valid_configs/vas_with_url.txt`
- Create: `tests/integration/test_fixture_configs.py`
- Modify: `tests/conftest.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `vtap100.roundtrip.compare`, `extract_settings` (Task 1)
- Produces: `valid_config_files()` — a module-level helper returning `list[Path]` used by `pytest.mark.parametrize`; later tasks add files to the directory and need no code change.

- [ ] **Step 1: Create the two starting fixtures**

An empty configuration is deliberately **not** part of the corpus: it carries no
setting to preserve, so it tests nothing the other fixtures do not. Create two
files the tool already handles today, so this task ends green.

Create `tests/fixtures/valid_configs/vas_basic.txt`:

```
!VTAPconfig

; A single Apple VAS pass in slot 1.
VAS1MerchantID=pass.com.example.basic
VAS1KeySlot=1
```

Create `tests/fixtures/valid_configs/vas_with_url.txt`:

```
!VTAPconfig

; MerchantURL is optional and already supported today.
VAS1MerchantID=pass.com.example.basic
VAS1KeySlot=1
VAS1MerchantURL=https://example.com/pass
```

- [ ] **Step 2: Write the failing test**

Create `tests/integration/test_fixture_configs.py`:

```python
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
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `uv run --extra dev pytest tests/integration/test_fixture_configs.py -q`
Expected: FAIL at collection — `ModuleNotFoundError` if Task 1 was skipped, otherwise `FileNotFoundError` for `tests/fixtures/valid_configs` if Step 1 was skipped.

- [ ] **Step 4: Wire conftest to the real directories**

`tests/conftest.py` already defines `fixtures_dir`, `valid_configs_dir`, `invalid_configs_dir` and `expected_outputs_dir` pointing at `tests/fixtures/`. They were dead because the directory never existed. Leave the fixture definitions exactly as they are — creating the directory is what makes them work. Add one new fixture at the end of the file:

```python
@pytest.fixture
def local_configs_dir(fixtures_dir: Path) -> Path:
    """Return path to the git-ignored private config corpus."""
    return fixtures_dir / "local_configs"
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run --extra dev pytest tests/integration/test_fixture_configs.py -q`
Expected: PASS, 8 tests (2 fixtures x 4 checks).

- [ ] **Step 6: Protect key material**

Add to `.gitignore`, under the existing "Generated config files" section:

```
# Key material — never commit
*.pem
*.key
appkey*.txt
```

- [ ] **Step 7: Verify nothing sensitive is tracked**

Run: `git check-ignore -v test.pem appkey1.txt`
Expected: both reported as ignored by the new rules.

- [ ] **Step 8: Commit**

```bash
git add tests/fixtures tests/integration/test_fixture_configs.py tests/conftest.py .gitignore
git commit -m "test: add fixture corpus and round-trip battery

Creates tests/fixtures/, which conftest.py has pointed at since the
beginning without it ever existing — its four fixtures were dead.

The battery is parametrised by glob, so a configuration dropped into
valid_configs/ is subjected to all four checks with no change to test
code. Later tasks add one fixture each.

Also ignores *.pem, *.key and appkey*.txt: this repository is public
and its subject matter is key slots."
```

---

## Task 2b: Fixture leak check as a pre-commit hook

Anonymisation must not depend on anyone remembering it. This repository is
public, and a missed identifier is permanent — it stays in the history even
after the file is corrected. A hook makes forgetting impossible rather than
unlikely, and it also covers the path that never runs `anonymize` at all:
copying a real file straight into `valid_configs/`.

The check is an **allowlist, not a deny list**. A deny list would have to name
the real merchant IDs, collector IDs and AIDs it is meant to keep out — which
would publish them in this very file. An allowlist names only the placeholders,
so adding a genuinely new example value is a deliberate edit, and that edit is
exactly the moment to notice whether the value is real.

**Files:**
- Create: `scripts/check_fixture_leaks.py`
- Create: `tests/unit/test_fixture_leak_check.py`
- Modify: `.pre-commit-config.yaml`
- Modify: `pyproject.toml` (`pythonpath`)

**Interfaces:**
- Produces: `check_file(path: Path) -> list[str]` returning one message per
  violation, empty when clean; `main(argv: list[str]) -> int` returning 1 when
  any file has a violation.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_fixture_leak_check.py`:

```python
"""Unit tests for the fixture leak check.

The check is an allowlist: fixtures may only contain placeholder identifiers.
"""

import pytest


class TestCheckFile:
    """Violations that must be caught before a commit reaches a public repo."""

    def test_clean_fixture_passes(self, tmp_path) -> None:
        """A fixture using only placeholders is accepted."""
        from check_fixture_leaks import check_file

        f = tmp_path / "clean.txt"
        f.write_text(
            "!VTAPconfig\n"
            "VAS2MerchantID=pass.com.example.library-card\n"
            "ST2CollectorID=12345678\n"
            "DESFire1AppID=AABBCC\n"
            "AccessTCI=020000\n"
        )
        assert check_file(f) == []

    def test_key_material_is_rejected(self, tmp_path) -> None:
        """A PEM block must never be committed, whatever the file is called."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("-----BEGIN EC PRIVATE KEY-----\nMHcCAQ\n")
        assert any("key material" in m for m in check_file(f))

    def test_real_merchant_id_is_rejected(self, tmp_path) -> None:
        """Merchant IDs must sit under pass.com.example."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("!VTAPconfig\nVAS2MerchantID=pass.de.somewhere.library-card\n")
        messages = check_file(f)
        assert any("MerchantID" in m for m in messages)

    def test_unlisted_collector_id_is_rejected(self, tmp_path) -> None:
        """Collector IDs must come from the placeholder set."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("!VTAPconfig\nST2CollectorID=99887766\n")
        assert any("CollectorID" in m for m in check_file(f))

    def test_unlisted_app_id_is_rejected(self, tmp_path) -> None:
        """DESFire AIDs must come from the placeholder set."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("!VTAPconfig\nDESFire1AppID=D0FFEE\n")
        assert any("AppID" in m for m in check_file(f))

    def test_long_hex_in_comment_is_rejected(self, tmp_path) -> None:
        """A System Identifier blob in a comment is still an identifier."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("; SysID: 4E4F545F415F5245414C5F5359534944 (16B)\n")
        assert any("hex" in m for m in check_file(f))

    def test_placeholder_sysid_in_comment_passes(self, tmp_path) -> None:
        """The placeholder System Identifier is allowed."""
        from check_fixture_leaks import check_file

        f = tmp_path / "clean.txt"
        f.write_text("; SysID: 4558414D504C455F7379735F31303030 (16B)\n")
        assert check_file(f) == []


class TestMain:
    """Exit code contract for pre-commit."""

    def test_returns_one_when_a_file_leaks(self, tmp_path) -> None:
        """A violation fails the commit."""
        from check_fixture_leaks import main

        f = tmp_path / "leak.txt"
        f.write_text("-----BEGIN EC PRIVATE KEY-----\n")
        assert main([str(f)]) == 1

    def test_returns_zero_when_clean(self, tmp_path) -> None:
        """No violation, no obstruction."""
        from check_fixture_leaks import main

        f = tmp_path / "clean.txt"
        f.write_text("!VTAPconfig\nVAS1MerchantID=pass.com.example.x\n")
        assert main([str(f)]) == 0
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run --extra dev pytest tests/unit/test_fixture_leak_check.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'check_fixture_leaks'`.

- [ ] **Step 3: Write the checker**

Create `scripts/check_fixture_leaks.py`:

```python
"""Reject real deployment identifiers in committed test fixtures.

This repository is public and its subject matter is key slots and wallet
credentials. A deployment identifier committed by accident stays in the history
even after the file is corrected, so the check runs as a pre-commit hook rather
than as a step someone has to remember.

The rules are an allowlist. A deny list would have to name the real identifiers
it keeps out, publishing them in this file; an allowlist names only the
placeholders, so introducing a new example value is a deliberate edit.
"""

from pathlib import Path
import re
import sys


ALLOWED_MERCHANT_PREFIX = "pass.com.example."
ALLOWED_COLLECTOR_IDS = {"12345678", "87654321"}
ALLOWED_APP_IDS = {"AABBCC"}
ALLOWED_TCIS = {"020000", "030000", "02AB40"}
# EXAMPLE_sys_1000 in hex — the placeholder System Identifier.
ALLOWED_HEX_BLOBS = {"4558414D504C455F7379735F31303030"}

MERCHANT_ID = re.compile(r"^VAS\d*MerchantID=(.+)$")
COLLECTOR_ID = re.compile(r"^ST\d*CollectorID=(.+)$")
APP_ID = re.compile(r"^DESFire\d*AppID=(.+)$")
ACCESS_TCI = re.compile(r"^AccessTCI=(.+)$")
LONG_HEX = re.compile(r"[0-9A-Fa-f]{24,}")


def check_file(path: Path) -> list[str]:
    """Check one file for identifiers that must not reach a public repository.

    Args:
        path: File to inspect.

    Returns:
        One message per violation; empty when the file is clean.
    """
    problems: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return problems

    for number, line in enumerate(text.splitlines(), start=1):
        where = f"{path}:{number}"

        if "-----BEGIN" in line:
            problems.append(f"{where}: key material must never be committed")
            continue

        stripped = line.strip()

        if match := MERCHANT_ID.match(stripped):
            if not match.group(1).startswith(ALLOWED_MERCHANT_PREFIX):
                problems.append(
                    f"{where}: MerchantID must start with {ALLOWED_MERCHANT_PREFIX!r}"
                )
        elif match := COLLECTOR_ID.match(stripped):
            if match.group(1) not in ALLOWED_COLLECTOR_IDS:
                problems.append(f"{where}: CollectorID is not a known placeholder")
        elif match := APP_ID.match(stripped):
            if match.group(1).upper() not in ALLOWED_APP_IDS:
                problems.append(f"{where}: DESFire AppID is not a known placeholder")
        elif match := ACCESS_TCI.match(stripped):
            if match.group(1).upper() not in ALLOWED_TCIS:
                problems.append(f"{where}: AccessTCI is not a known placeholder")

        for blob in LONG_HEX.findall(line):
            if blob.upper() not in {b.upper() for b in ALLOWED_HEX_BLOBS}:
                problems.append(f"{where}: long hex value is not a known placeholder")

    return problems


def main(argv: list[str]) -> int:
    """Check every given file.

    Args:
        argv: Paths to check, as pre-commit passes them.

    Returns:
        1 if any file has a violation, otherwise 0.
    """
    problems: list[str] = []
    for name in argv:
        problems.extend(check_file(Path(name)))

    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(
            "\nFixtures must use placeholder identifiers only. "
            "Run 'vtap100 anonymize' or extend the allowlist in "
            "scripts/check_fixture_leaks.py if the value really is an example.",
            file=sys.stderr,
        )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

Note the comment naming the AID case-insensitively: real fixtures write `AABBCC` in the settings and `aabbcc` in the generator's comment header, and both must pass.

- [ ] **Step 4: Make the script importable from tests**

In `pyproject.toml`, extend the pytest path so the test can import the module:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "scripts"]
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run --extra dev pytest tests/unit/test_fixture_leak_check.py -q`
Expected: PASS, 9 tests.

- [ ] **Step 6: Wire it into pre-commit**

Append to `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: fixture-leak-check
        name: Reject real identifiers in test fixtures
        entry: python scripts/check_fixture_leaks.py
        language: system
        files: ^tests/fixtures/
```

`files:` scopes it to the fixture corpus. `local_configs/` is git-ignored and can never be staged, so the hook never sees it.

- [ ] **Step 7: Verify the hook actually blocks**

```bash
printf -- '-----BEGIN EC PRIVATE KEY-----\n' > tests/fixtures/valid_configs/leak_probe.txt
git add tests/fixtures/valid_configs/leak_probe.txt
uv run --extra dev pre-commit run fixture-leak-check --files tests/fixtures/valid_configs/leak_probe.txt
```

Expected: the hook fails and names the file. Then remove the probe:

```bash
git restore --staged tests/fixtures/valid_configs/leak_probe.txt
rm tests/fixtures/valid_configs/leak_probe.txt
```

Do not skip this step. A hook nobody has watched fail is a hook nobody knows works.

- [ ] **Step 8: Commit**

```bash
git add scripts/check_fixture_leaks.py tests/unit/test_fixture_leak_check.py .pre-commit-config.yaml pyproject.toml
git commit -m "test: reject real identifiers in fixtures at commit time

Anonymisation was a command someone had to remember, with a manual
grep as the only backstop. This repository is public and a leaked
identifier stays in the history after the file is fixed, so the check
belongs in a hook.

It is an allowlist, not a deny list: a deny list would have to name
the real merchant IDs, collector IDs and AIDs it keeps out, publishing
them in the checker itself. An allowlist names only placeholders, so
adding a new example value is a deliberate edit — and that edit is
where someone notices the value is real."
```

---

## Task 3: DESFire FileID accepts 0

The single constraint blocking 14 of 17 real configurations.

**Files:**
- Modify: `src/vtap100/models/desfire.py:51`
- Create: `tests/fixtures/valid_configs/desfire_fileid_zero.txt`
- Test: `tests/unit/test_models_desfire.py`

**Interfaces:**
- Produces: `DESFireAppConfig.file_id` accepting `0..255`.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_models_desfire.py`:

```python
class TestDESFireFileIdRange:
    """FileID range per the manufacturer: 'Use a value from 0 to 255'."""

    def test_file_id_zero_is_valid(self) -> None:
        """File 0 is a legal DESFire file number and appears in real configs."""
        from vtap100.models.desfire import DESFireAppConfig

        config = DESFireAppConfig(app_id="AABBCC", file_id=0)
        assert config.file_id == 0

    def test_file_id_255_is_valid(self) -> None:
        """Upper bound is inclusive."""
        from vtap100.models.desfire import DESFireAppConfig

        assert DESFireAppConfig(app_id="AABBCC", file_id=255).file_id == 255

    def test_file_id_256_is_rejected(self) -> None:
        """Above the documented range is still an error."""
        import pytest
        from pydantic import ValidationError
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", file_id=256)
```

- [ ] **Step 2: Add the fixture**

Create `tests/fixtures/valid_configs/desfire_fileid_zero.txt`:

```
!VTAPconfig

; DESFire read from file 0 — the form used by real deployments.
NFCType4=D

DESFire1AppID=AABBCC
DESFire1FileID=0
DESFire1Crypto=3
DESFire1KeyNum=2
DESFire1KeySlot=2
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_models_desfire.py::TestDESFireFileIdRange tests/integration/test_fixture_configs.py -q`
Expected: FAIL — `file_id: Input should be greater than or equal to 1` for both the unit test and the new fixture.

- [ ] **Step 4: Fix the constraint**

In `src/vtap100/models/desfire.py`, change line 51 from:

```python
    file_id: int | None = Field(default=None, ge=1, le=255, description="File ID (1-255)")
```

to:

```python
    file_id: int | None = Field(default=None, ge=0, le=255, description="File ID (0-255)")
```

Also update the docstring attribute line above (currently `file_id: File ID to read (1-255).`) to say `(0-255)`.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run --extra dev pytest tests/unit/test_models_desfire.py tests/integration/test_fixture_configs.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/vtap100/models/desfire.py tests/unit/test_models_desfire.py tests/fixtures
git commit -m "fix: accept DESFire FileID 0

The manufacturer documents 'Use a value from 0 to 255'; the model
required 1. File 0 is a legal DESFire file number and is what real
deployments use, so this single constraint made 14 of 17 real
configurations unloadable."
```

---

## Task 4: VAS and Smart Tap KeySlot become optional

**Files:**
- Modify: `src/vtap100/models/vas.py:43-48`, `src/vtap100/models/smarttap.py:47-58`
- Modify: `src/vtap100/parser.py:47`, `:57-58` (`_VASParseData`, `_SmartTapParseData` defaults)
- Create: `tests/fixtures/valid_configs/vas_keyslot_omitted.txt`, `tests/fixtures/valid_configs/vas_keyslot_zero.txt`
- Test: `tests/unit/test_models_vas.py`, `tests/unit/test_models_smarttap.py`

**Interfaces:**
- Produces: `AppleVASConfig.key_slot: int | None` and `GoogleSmartTapConfig.key_slot: int | None`, both `ge=0, le=6`, default `None`. `to_config_lines` omits the `KeySlot` line when the value is `None`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/unit/test_models_vas.py`:

```python
class TestVASKeySlotOptional:
    """KeySlot per the manufacturer: '=0 or omitted (default)'."""

    def test_key_slot_may_be_omitted(self) -> None:
        """A VAS config without a key slot is valid; the reader auto-selects."""
        from vtap100.models.vas import AppleVASConfig

        config = AppleVASConfig(merchant_id="pass.com.example.x")
        assert config.key_slot is None

    def test_key_slot_zero_is_valid(self) -> None:
        """Zero means automatic key selection."""
        from vtap100.models.vas import AppleVASConfig

        assert AppleVASConfig(merchant_id="pass.com.example.x", key_slot=0).key_slot == 0

    def test_key_slot_seven_is_rejected(self) -> None:
        """Above the documented range is an error."""
        import pytest
        from pydantic import ValidationError
        from vtap100.models.vas import AppleVASConfig

        with pytest.raises(ValidationError):
            AppleVASConfig(merchant_id="pass.com.example.x", key_slot=7)

    def test_omitted_key_slot_emits_no_line(self) -> None:
        """An absent key slot must not appear in the output."""
        from vtap100.models.vas import AppleVASConfig

        lines = AppleVASConfig(merchant_id="pass.com.example.x").to_config_lines(1)
        assert lines == ["VAS1MerchantID=pass.com.example.x"]
```

Append the equivalent class to `tests/unit/test_models_smarttap.py`, using `GoogleSmartTapConfig(collector_id="12345678")` and expecting `["ST2CollectorID=12345678"]` from `to_config_lines(2)`.

**Ordering note:** `slot` does not exist yet — Task 5 adds it. These tests
therefore construct the models without it, and Task 5 Step 7 updates them along
with every other call site when the field becomes required. Do not add `slot=`
here.

- [ ] **Step 2: Add the fixtures**

Create `tests/fixtures/valid_configs/vas_keyslot_omitted.txt`:

```
!VTAPconfig

; The manufacturer documents KeySlot as optional: with no slot given,
; all available keys are compared against the hash of the public key.
VAS1MerchantID=pass.com.example.autokey
```

Create `tests/fixtures/valid_configs/vas_keyslot_zero.txt`:

```
!VTAPconfig

; KeySlot=0 is the documented spelling of automatic key selection.
VAS1MerchantID=pass.com.example.autokey
VAS1KeySlot=0
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_models_vas.py tests/unit/test_models_smarttap.py tests/integration/test_fixture_configs.py -q`
Expected: FAIL — validation errors for the missing/zero key slot.

- [ ] **Step 4: Relax the model constraints**

In `src/vtap100/models/vas.py`, replace the `key_slot` field with:

```python
    key_slot: int | None = Field(
        default=None,
        ge=0,
        le=6,
        description="Private key slot (0-6; 0 or omitted means automatic selection)",
    )
```

In `to_config_lines`, replace the unconditional key-slot append with:

```python
        if self.key_slot is not None:
            lines.append(f"VAS{slot_number}KeySlot={self.key_slot}")
```

Apply the same two changes in `src/vtap100/models/smarttap.py` for `key_slot`, and make `key_version` optional the same way (`int | None`, `default=None`), emitting its line only when set.

- [ ] **Step 5: Stop the parser inventing a key slot**

In `src/vtap100/parser.py`, change `_VASParseData.key_slot` and `_SmartTapParseData.key_slot`/`key_version` from `int = 0` to `int | None = None`, so "absent from the file" and "explicitly zero" stay distinguishable.

- [ ] **Step 6: Run the tests to verify they pass**

Run: `uv run --extra dev pytest -q`
Expected: PASS. Existing tests that construct these models without `slot=` will fail until Task 5 — if you are running tasks in order, expect those failures here and resolve them in Task 5.

- [ ] **Step 7: Commit**

```bash
git add src/vtap100/models/vas.py src/vtap100/models/smarttap.py src/vtap100/parser.py tests/
git commit -m "fix: VAS and Smart Tap KeySlot are optional

The manufacturer documents '=1 to =6, identifying key file. =0 or
omitted (default)' for both. Commit f43eb0c made the field required,
which was a regression against the specification — the repository
documentation it contradicted had been correct.

The parser also defaulted the field to 0 before validating, so a file
with no KeySlot line could not be distinguished from one setting it
to zero."
```

---

## Task 5: Slot numbers survive the round-trip

**Files:**
- Modify: `src/vtap100/models/vas.py`, `src/vtap100/models/smarttap.py` (add `slot`)
- Modify: `src/vtap100/parser.py:546-568` (`_build_config`)
- Modify: `src/vtap100/generator.py:125-126`, `:136-137`
- Create: `tests/fixtures/valid_configs/slots_two_and_three.txt`

**Interfaces:**
- Produces: `AppleVASConfig.slot: int` and `GoogleSmartTapConfig.slot: int`, both required, `ge=1, le=6`. `to_config_lines(slot_number)` keeps its signature so existing callers still work.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_parser.py`:

```python
class TestSlotPreservation:
    """Pass slot numbers must survive parse and regenerate."""

    def test_vas_slot_is_captured(self) -> None:
        """VAS2 stays slot 2 in the model."""
        from vtap100.parser import parse

        config = parse("!VTAPconfig\nVAS2MerchantID=pass.com.example.x\nVAS2KeySlot=2\n")
        assert config.vas_configs[0].slot == 2

    def test_smarttap_slot_is_captured(self) -> None:
        """ST3 stays slot 3 in the model."""
        from vtap100.parser import parse

        config = parse("!VTAPconfig\nST3CollectorID=12345678\nST3KeySlot=3\n")
        assert config.smarttap_configs[0].slot == 3

    def test_slots_are_not_renumbered(self) -> None:
        """Regenerating writes back the original slot numbers."""
        from vtap100.generator import ConfigGenerator
        from vtap100.parser import parse

        text = "!VTAPconfig\nVAS2MerchantID=pass.com.example.x\nST3CollectorID=12345678\n"
        out = ConfigGenerator(parse(text)).generate()
        assert "VAS2MerchantID" in out
        assert "ST3CollectorID" in out
        assert "VAS1MerchantID" not in out
        assert "ST2CollectorID" not in out

    def test_smarttap_slot_one_is_preserved(self) -> None:
        """ST1 is written back as ST1, not silently moved to ST2.

        ST1 does not work on real readers (see d18c8c4) and config creation
        still avoids it, but rewriting a file the user asked us to load is a
        silent change to their configuration.
        """
        from vtap100.generator import ConfigGenerator
        from vtap100.parser import parse

        out = ConfigGenerator(parse("!VTAPconfig\nST1CollectorID=80644855\n")).generate()
        assert "ST1CollectorID=80644855" in out
```

- [ ] **Step 2: Add the fixture**

Create `tests/fixtures/valid_configs/slots_two_and_three.txt`:

```
!VTAPconfig

; Pass slots need not start at 1 or be contiguous. The slot number is a
; grouping index; the key slot it points at is independent.
VAS2MerchantID=pass.com.example.library-card
VAS2KeySlot=2

ST3CollectorID=12345678
ST3KeySlot=3
ST3KeyVersion=1
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_parser.py::TestSlotPreservation -q`
Expected: FAIL — `'AppleVASConfig' object has no attribute 'slot'`.

- [ ] **Step 4: Add the field to both models**

In `src/vtap100/models/vas.py`, add as the first field of `AppleVASConfig`:

```python
    slot: int = Field(
        ...,
        ge=1,
        le=6,
        description="Pass slot number (1-6) used in the VAS# parameter names",
    )
```

Add the identical field to `GoogleSmartTapConfig` in `src/vtap100/models/smarttap.py`, with the description naming `ST#`.

- [ ] **Step 5: Pass the slot through the parser**

In `src/vtap100/parser.py`, in `_build_config`, the loops already iterate `sorted(self._vas_data.keys())` — the slot is in hand and simply discarded. Add it to both constructor calls:

```python
        for slot in sorted(self._vas_data.keys()):
            data = self._vas_data[slot]
            if data.merchant_id:
                vas_configs.append(
                    AppleVASConfig(
                        slot=slot,
                        merchant_id=data.merchant_id,
                        key_slot=data.key_slot,
                        merchant_url=data.merchant_url,
                    )
                )
```

and likewise `slot=slot` for `GoogleSmartTapConfig`.

- [ ] **Step 6: Stop the generator renumbering**

In `src/vtap100/generator.py`, replace the two enumerate loops:

```python
        # Apple VAS configurations
        if self.config.vas_configs:
            lines.append("; Apple VAS Configuration")
            for vas in self.config.vas_configs:
                lines.extend(vas.to_config_lines(slot_number=vas.slot))
```

```python
        # Google Smart Tap configurations
        # Slot numbers come from the model. New configurations default to slot 2
        # because ST1 does not work on real readers, but a slot read from a file
        # is written back unchanged rather than silently moved.
        if self.config.smarttap_configs:
            lines.append("; Google Smart Tap Configuration")
            for st in self.config.smarttap_configs:
                lines.extend(st.to_config_lines(slot_number=st.slot))
```

- [ ] **Step 7: Fix existing call sites**

Run: `uv run --extra dev pytest -q 2>&1 | grep -c "slot"` to see how many tests construct these models without `slot=`.
Add `slot=1` (or the slot the test's config text implies) to every `AppleVASConfig(...)` and `GoogleSmartTapConfig(...)` construction in `tests/` and in `src/vtap100/tui/` that now fails. Do not give `slot` a default — a default would silently reintroduce renumbering for models built in code.

- [ ] **Step 8: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add -A src tests
git commit -m "fix: preserve pass slot numbers through a round-trip

VAS2 became VAS1 and ST3 became ST2 because the models carried no
slot and the generator re-derived it from list position. The parser
had the number in hand and discarded it.

ST1 is now written back as ST1. The finding behind d18c8c4 stands and
config creation still avoids slot 1, but rewriting a slot read from a
user's file is a silent change to their configuration — which is the
class of defect this work exists to remove."
```

---

## Task 6: Diversification becomes a bit field

**Files:**
- Modify: `src/vtap100/models/desfire.py:58` and add `DiversificationBuilder`
- Modify: `src/vtap100/parser.py:437`
- Modify: `src/vtap100/tui/widgets/forms/desfire.py:203-204`, `:250`, `:261`
- Modify: `src/vtap100/tui/i18n/translations/de.yaml`, `en.yaml`
- Create: `tests/fixtures/valid_configs/desfire_diversification.txt`

**Interfaces:**
- Produces: `DESFireAppConfig.diversification: int | None` (`ge=0, le=7`, valid when `0` or bit 0 set); `DiversificationBuilder` with `ACTIVE = 0b001`, `OMIT_AID = 0b010`, `REVERSE_UID = 0b100`, methods `active()`, `omit_aid()`, `reverse_uid()`, `build() -> int`.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_models_desfire.py`:

```python
class TestDiversificationBitField:
    """Diversification is a bit field, not a switch.

    Bit 0 enables AN10922, bit 1 omits the AID from the input, bit 2 reverses
    UID byte order. Valid values are therefore 0, 1, 3, 5 and 7.
    """

    @pytest.mark.parametrize("value", [0, 1, 3, 5, 7])
    def test_documented_values_are_accepted(self, value: int) -> None:
        """Every documented mode is valid."""
        from vtap100.models.desfire import DESFireAppConfig

        assert DESFireAppConfig(app_id="AABBCC", diversification=value).diversification == value

    @pytest.mark.parametrize("value", [2, 4, 6])
    def test_modifier_without_active_bit_is_rejected(self, value: int) -> None:
        """A modifier bit without bit 0 means nothing."""
        from pydantic import ValidationError
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", diversification=value)

    def test_out_of_range_is_rejected(self) -> None:
        """Only three bits exist."""
        from pydantic import ValidationError
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", diversification=8)

    def test_builder_composes_bits(self) -> None:
        """The builder mirrors KBSourceBuilder for the other bitmask setting."""
        from vtap100.models.desfire import DiversificationBuilder

        assert DiversificationBuilder().active().build() == 1
        assert DiversificationBuilder().active().omit_aid().build() == 3
        assert DiversificationBuilder().active().reverse_uid().build() == 5
        assert DiversificationBuilder().active().omit_aid().reverse_uid().build() == 7
```

Append to `tests/unit/test_parser.py`:

```python
class TestDiversificationRoundTrip:
    """Every diversification mode must survive a cycle."""

    @pytest.mark.parametrize("value", [1, 3, 5, 7])
    def test_mode_is_preserved(self, value: int) -> None:
        """Modes 3, 5 and 7 were silently coerced to False and dropped."""
        from vtap100.generator import ConfigGenerator
        from vtap100.parser import parse

        text = f"!VTAPconfig\nDESFire1AppID=AABBCC\nDESFire1Diversification={value}\n"
        out = ConfigGenerator(parse(text)).generate()
        assert f"DESFire1Diversification={value}" in out
```

- [ ] **Step 2: Add the fixture**

Create `tests/fixtures/valid_configs/desfire_diversification.txt`:

```
!VTAPconfig

; Diversification bit field: bit 0 active, bit 1 omit AID, bit 2 reverse UID.
; Mode 5 means AN10922 with reversed UID byte order and the AID included.
NFCType4=D

DESFire1AppID=AABBCC
DESFire1FileID=0
DESFire1Diversification=5
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_models_desfire.py::TestDiversificationBitField tests/unit/test_parser.py::TestDiversificationRoundTrip -q`
Expected: FAIL — `DiversificationBuilder` does not exist; modes 3/5/7 come back as `1` or vanish.

- [ ] **Step 4: Change the model**

In `src/vtap100/models/desfire.py`, replace the `diversification` field:

```python
    diversification: int | None = Field(
        default=None,
        ge=0,
        le=7,
        description="Key diversification bit field (0, 1, 3, 5 or 7)",
    )
```

Add the validator alongside the existing `validate_app_id`:

```python
    @field_validator("diversification")
    @classmethod
    def validate_diversification(cls, v: int | None) -> int | None:
        """Reject modifier bits without the active bit.

        Bit 1 (omit AID) and bit 2 (reverse UID) modify how the AN10922 input is
        built. Setting either without bit 0 describes modifiers on a disabled
        feature, which the reader cannot act on.

        Args:
            v: The raw diversification value.

        Returns:
            The validated value.

        Raises:
            ValueError: If a modifier bit is set without bit 0.
        """
        if v is not None and v != 0 and not v & DiversificationBuilder.ACTIVE:
            msg = "diversification must be 0, or have bit 0 set (valid: 0, 1, 3, 5, 7)"
            raise ValueError(msg)
        return v
```

Add the builder at module level, after the enums:

```python
class DiversificationBuilder:
    """Builder for DESFire#Diversification bit field values.

    Mirrors KBSourceBuilder, the other bitmask setting in this codebase.

    - Bit 0 (0b001): AN10922 key diversification active
    - Bit 1 (0b010): omit the AID from the diversification input
    - Bit 2 (0b100): reverse UID byte order

    Reference:
        https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-DESFire-settings.htm

    Example:
        >>> DiversificationBuilder().active().reverse_uid().build()
        5
    """

    ACTIVE = 0b001
    OMIT_AID = 0b010
    REVERSE_UID = 0b100

    def __init__(self) -> None:
        """Initialise an empty builder with value 0."""
        self._value: int = 0

    def active(self) -> "DiversificationBuilder":
        """Enable AN10922 key diversification."""
        self._value |= self.ACTIVE
        return self

    def omit_aid(self) -> "DiversificationBuilder":
        """Omit the AID from the diversification input."""
        self._value |= self.OMIT_AID
        return self

    def reverse_uid(self) -> "DiversificationBuilder":
        """Reverse UID byte order."""
        self._value |= self.REVERSE_UID
        return self

    def build(self) -> int:
        """Return the composed bit field value."""
        return self._value
```

In `to_config_lines`, emit the integer instead of a boolean:

```python
        if self.diversification is not None:
            lines.append(f"{prefix}Diversification={self.diversification}")
```

- [ ] **Step 5: Change the parser**

In `src/vtap100/parser.py`, change the `_DESFireAppParseData.diversification` type from `bool | None` to `int | None`, and line 437 from:

```python
            self._get_desfire_app_data(slot).diversification = match.group(2) == "1"
```

to:

```python
            self._get_desfire_app_data(slot).diversification = int(match.group(2))
```

- [ ] **Step 6: Adapt the TUI form**

In `src/vtap100/tui/widgets/forms/desfire.py`, replace the single `Switch` with three checkboxes. Replace lines 203-204:

```python
            yield Label(t("forms.desfire.diversification"))
            yield Checkbox(
                t("forms.desfire.diversification_active"),
                value=bool(self._config.diversification),
                id="div_active",
            )
            yield Checkbox(
                t("forms.desfire.diversification_omit_aid"),
                value=bool((self._config.diversification or 0) & DiversificationBuilder.OMIT_AID),
                id="div_omit_aid",
            )
            yield Checkbox(
                t("forms.desfire.diversification_reverse_uid"),
                value=bool((self._config.diversification or 0) & DiversificationBuilder.REVERSE_UID),
                id="div_reverse_uid",
            )
```

Replace the read at line 250 and the construction at line 261:

```python
        builder = DiversificationBuilder()
        if self.query_one("#div_active", Checkbox).value:
            builder.active()
            if self.query_one("#div_omit_aid", Checkbox).value:
                builder.omit_aid()
            if self.query_one("#div_reverse_uid", Checkbox).value:
                builder.reverse_uid()
        diversification = builder.build() or None
```

Import `Checkbox` from `textual.widgets` and `DiversificationBuilder` from `vtap100.models.desfire` at the top of the file.

- [ ] **Step 7: Add the bilingual labels**

Under `forms.desfire` in both `src/vtap100/tui/i18n/translations/en.yaml` and `de.yaml`, replacing the existing single `diversification` label:

English:
```yaml
    diversification: "Diversification"
    diversification_active: "Key diversification (AN10922)"
    diversification_omit_aid: "Omit AID from input"
    diversification_reverse_uid: "Reverse UID byte order"
```

German:
```yaml
    diversification: "Diversifikation"
    diversification_active: "Schlüssel-Diversifikation (AN10922)"
    diversification_omit_aid: "AID nicht einbeziehen"
    diversification_reverse_uid: "UID-Byte-Reihenfolge umkehren"
```

- [ ] **Step 8: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS. Update the existing `test_parse_desfire_diversification` in `tests/unit/test_parser.py:528`, which asserts `is True` — it must now assert `== 1`.

- [ ] **Step 9: Commit**

```bash
git add -A src tests
git commit -m "fix: treat DESFire diversification as the bit field it is

Bit 0 activates AN10922, bit 1 omits the AID from the diversification
input, bit 2 reverses UID byte order. Modelling it as a bool coerced
modes 3, 5 and 7 to False and dropped the line entirely on save.

That failure is silent and severe: the reader computes a different
diversified key and authentication simply stops working, with nothing
to indicate why.

The UI becomes three checkboxes rather than a five-item dropdown, so
it mirrors the semantics, and DiversificationBuilder follows the
KBSourceBuilder pattern already used for the other bitmask setting."
```

---

## Task 7: Remaining DESFire range constraints

**Files:**
- Modify: `src/vtap100/models/desfire.py:52`, `:60-61`
- Create: `tests/fixtures/invalid_configs/desfire_keynum_16.txt`, `desfire_keyslot_10.txt`, `desfire_fileid_256.txt`
- Create: `tests/integration/test_invalid_configs.py`

**Interfaces:**
- Produces: `key_num` `ge=0, le=15`; `sysid_key_slot` `ge=0, le=9`; `privacy_key_slot` `ge=1, le=9`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/unit/test_models_desfire.py`:

```python
class TestDESFireRemainingRanges:
    """Ranges the model left unchecked."""

    @pytest.mark.parametrize(
        ("field_name", "valid", "invalid"),
        [
            ("key_num", 15, 16),
            ("sysid_key_slot", 9, 10),
            ("privacy_key_slot", 9, 10),
        ],
    )
    def test_upper_bound(self, field_name: str, valid: int, invalid: int) -> None:
        """The documented upper bound is enforced."""
        from pydantic import ValidationError
        from vtap100.models.desfire import DESFireAppConfig

        assert getattr(DESFireAppConfig(app_id="AABBCC", **{field_name: valid}), field_name) == valid
        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", **{field_name: invalid})

    def test_privacy_key_slot_zero_is_rejected(self) -> None:
        """Privacy key slots are 1-9; there is no 'none' value."""
        from pydantic import ValidationError
        from vtap100.models.desfire import DESFireAppConfig

        with pytest.raises(ValidationError):
            DESFireAppConfig(app_id="AABBCC", privacy_key_slot=0)

    def test_sysid_key_slot_zero_is_valid(self) -> None:
        """SysIDKeySlot=0 means 'do not use a System Identifier'."""
        from vtap100.models.desfire import DESFireAppConfig

        assert DESFireAppConfig(app_id="AABBCC", sysid_key_slot=0).sysid_key_slot == 0
```

- [ ] **Step 2: Create the rejection battery**

Create `tests/integration/test_invalid_configs.py`:

```python
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
```

- [ ] **Step 3: Create the invalid fixtures**

`tests/fixtures/invalid_configs/desfire_fileid_256.txt`:
```
!VTAPconfig
DESFire1AppID=AABBCC
DESFire1FileID=256
```

`tests/fixtures/invalid_configs/desfire_keynum_16.txt`:
```
!VTAPconfig
DESFire1AppID=AABBCC
DESFire1KeyNum=16
```

`tests/fixtures/invalid_configs/desfire_keyslot_10.txt`:
```
!VTAPconfig
DESFire1AppID=AABBCC
DESFire1KeySlot=10
```

`tests/fixtures/invalid_configs/vas_keyslot_7.txt`:
```
!VTAPconfig
VAS1MerchantID=pass.com.example.x
VAS1KeySlot=7
```

`tests/fixtures/invalid_configs/vas_merchant_id_no_prefix.txt`:
```
!VTAPconfig
VAS1MerchantID=com.example.missing-pass-prefix
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_models_desfire.py::TestDESFireRemainingRanges tests/integration/test_invalid_configs.py -q`
Expected: FAIL — `key_num=16` and the two slot values are currently accepted.

- [ ] **Step 5: Add the constraints**

In `src/vtap100/models/desfire.py`:

```python
    key_num: int | None = Field(default=None, ge=0, le=15, description="Key number (0-15)")
    privacy_key_num: int | None = Field(default=None, ge=0, le=15, description="Privacy key number (0-15)")
    privacy_key_slot: int | None = Field(default=None, ge=1, le=9, description="Privacy key slot (1-9)")
    sysid_key_slot: int | None = Field(default=None, ge=0, le=9, description="System ID key slot (0-9)")
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add -A src tests
git commit -m "fix: enforce the documented DESFire ranges

KeyNum is 0-15, PrivacyKeySlot 1-9, SysIDKeySlot 0-9 where 0 means no
System Identifier. All three were unchecked, so invalid values reached
the reader unremarked.

Adds the rejection battery, which asserts the error names the field
responsible rather than merely that parsing failed."
```

---

*Tasks 8-15 continue in this document below.*

---

## Task 8: Keyboard — all eleven settings parsed and preserved

The parser has regexes for two of eleven keyboard settings. The other nine model fields exist but were never wired up, so `KBPostfix=%0D` is read as the default `%0A` and then dropped on save — after which the reader emits LF instead of CR.

**Files:**
- Modify: `src/vtap100/models/keyboard.py:47-95`
- Modify: `src/vtap100/parser.py:162-163` (regexes), `_KeyboardParseData`, `_parse_keyboard_line`, `_build_config`
- Create: `tests/fixtures/valid_configs/keyboard_full.txt`
- Test: `tests/unit/test_models_keyboard.py`, `tests/unit/test_parser.py`

**Interfaces:**
- Produces: `KeyboardConfig` with `enable`, `postfix`, `delay_ms`, `pass_mode`, `pass_section`, `pass_separator`, `pass_start`, `pass_length` all `T | None = None`. `to_config_lines()` emits a line only for fields that are not `None`.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_parser.py`:

```python
class TestKeyboardCompleteness:
    """All eleven KB settings must be parsed and preserved."""

    KB_CONFIG = (
        "!VTAPconfig\n"
        "KBLogMode=1\n"
        "KBEnable=1\n"
        "KBSource=81\n"
        "KBPrefix=%09\n"
        "KBPostfix=%0D\n"
        "KBDelayMS=2\n"
        "KBPassMode=1\n"
        "KBPassSection=2\n"
        "KBPassSeparator=;\n"
        "KBPassStart=3\n"
        "KBPassLength=14\n"
    )

    def test_postfix_is_parsed(self) -> None:
        """KBPostfix=%0D must not be read as the %0A default."""
        from vtap100.parser import parse

        assert parse(self.KB_CONFIG).keyboard.postfix == "%0D"

    def test_delay_below_documented_minimum_is_preserved(self) -> None:
        """Parsing is tolerant: the manufacturer's own sample uses 2."""
        from vtap100.parser import parse

        assert parse(self.KB_CONFIG).keyboard.delay_ms == 2

    def test_all_settings_survive_a_roundtrip(self) -> None:
        """No keyboard setting is lost."""
        from vtap100.roundtrip import compare

        report = compare(self.KB_CONFIG)
        assert report.lost == []
        assert report.changed == []

    def test_explicitly_set_default_is_preserved(self) -> None:
        """An explicit KBPostfix=%0A must keep its line."""
        from vtap100.roundtrip import compare

        report = compare("!VTAPconfig\nKBLogMode=1\nKBPostfix=%0A\n")
        assert report.lost == []
```

- [ ] **Step 2: Add the fixture**

Create `tests/fixtures/valid_configs/keyboard_full.txt`:

```
!VTAPconfig

; All eleven keyboard settings. KBDelayMS=2 is below the documented
; minimum of 5 and appears in the manufacturer's own sample file, so
; parsing preserves it rather than rejecting or clamping it.
KBLogMode=1
KBEnable=1
KBSource=81
KBPrefix=%09
KBPostfix=%0D
KBDelayMS=2
KBPassMode=1
KBPassSection=2
KBPassSeparator=;
KBPassStart=3
KBPassLength=14
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_parser.py::TestKeyboardCompleteness -q`
Expected: FAIL — `postfix` is `%0A`, `delay_ms` is `5`, nine settings reported lost.

- [ ] **Step 4: Make the fields optional**

In `src/vtap100/models/keyboard.py`, change these eight fields so absence is representable. Keep `log_mode` and `source` as they are:

```python
    enable: bool | None = Field(default=None, description="Enable USB keyboard device (KBEnable)")
    postfix: str | None = Field(default=None, max_length=80, description="Keystrokes appended after data (KBPostfix)")
    delay_ms: int | None = Field(default=None, ge=0, le=255, description="Inter-keystroke delay in ms (KBDelayMS)")
    pass_mode: bool | None = Field(default=None, description="Extract a delimited section (KBPassMode)")
    pass_section: int | None = Field(default=None, ge=0, description="Section number to read (KBPassSection)")
    pass_separator: str | None = Field(default=None, min_length=1, max_length=1, description="Section separator (KBPassSeparator)")
    pass_start: int | None = Field(default=None, ge=0, description="First character to read (KBPassStart)")
    pass_length: int | None = Field(default=None, ge=0, description="Number of characters to read (KBPassLength)")
```

`delay_ms` is deliberately `ge=0` rather than the documented `ge=5`: parsing is tolerant, and the TUI carries the strict bound. Note this in the field description as shown.

In `to_config_lines`, emit each of the eight only when not `None`, for example:

```python
        if self.postfix is not None:
            lines.append(f"KBPostfix={self.postfix}")
        if self.delay_ms is not None:
            lines.append(f"KBDelayMS={self.delay_ms}")
```

- [ ] **Step 5: Add the nine regexes**

In `src/vtap100/parser.py`, beside the two existing keyboard patterns:

```python
    KB_ENABLE = re.compile(r"^KBEnable=(\d+)$")
    KB_PREFIX = re.compile(r"^KBPrefix=(.*)$")
    KB_POSTFIX = re.compile(r"^KBPostfix=(.*)$")
    KB_DELAY_MS = re.compile(r"^KBDelayMS=(\d+)$")
    KB_PASS_MODE = re.compile(r"^KBPassMode=(\d+)$")
    KB_PASS_SECTION = re.compile(r"^KBPassSection=(\d+)$")
    KB_PASS_SEPARATOR = re.compile(r"^KBPassSeparator=(.)$")
    KB_PASS_START = re.compile(r"^KBPassStart=(\d+)$")
    KB_PASS_LENGTH = re.compile(r"^KBPassLength=(\d+)$")
```

Add the matching fields to `_KeyboardParseData`, all defaulting to `None`, and a branch per pattern in `_parse_keyboard_line` following the existing `if match := ...: ...; return True` style. `KB_PREFIX` and `KB_POSTFIX` use `(.*)` rather than `(.+)` so an empty value is captured rather than skipped.

- [ ] **Step 6: Pass them into the model**

In `_build_config`, replace the two-field `KeyboardConfig(...)` construction with one that forwards every parsed field, and widen the guard so a file with only, say, `KBPostfix` still produces a keyboard section:

```python
        kb = self._keyboard_data
        if any(
            value is not None
            for value in (
                kb.log_mode, kb.enable, kb.source, kb.prefix, kb.postfix, kb.delay_ms,
                kb.pass_mode, kb.pass_section, kb.pass_separator, kb.pass_start, kb.pass_length,
            )
        ):
            keyboard = KeyboardConfig(
                log_mode=kb.log_mode or False,
                enable=kb.enable,
                source=kb.source or "A5",
                prefix=kb.prefix,
                postfix=kb.postfix,
                delay_ms=kb.delay_ms,
                pass_mode=kb.pass_mode,
                pass_section=kb.pass_section,
                pass_separator=kb.pass_separator,
                pass_start=kb.pass_start,
                pass_length=kb.pass_length,
            )
```

- [ ] **Step 7: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS. Some existing TUI form tests read `config.keyboard.postfix` expecting a string; update them to handle `None`.

- [ ] **Step 8: Commit**

```bash
git add -A src tests
git commit -m "fix: parse all eleven keyboard settings

Only KBLogMode and KBSource had regexes. The other nine model fields
existed but were never wired up, so KBPostfix=%0D was read as the
default %0A and then dropped on save, silently switching the reader
from CR to LF.

The eight optional fields become T | None so an explicitly set default
keeps its line. KBDelayMS parses as 0-255 rather than the documented
5-255: the manufacturer's own sample file uses 2, so tolerance here is
what it takes to load the vendor's reference config."
```

---

## Task 9: LED and beep short forms

**Files:**
- Modify: `src/vtap100/models/feedback.py:44-46`, `:78-80`
- Modify: `src/vtap100/parser.py:770-790` (`_parse_beep_sequence`, `_parse_led_sequence`)
- Create: `tests/fixtures/valid_configs/feedback_short_forms.txt`

**Interfaces:**
- Produces: `LEDSequence.off_ms`/`repeats` and `BeepSequence.off_ms`/`repeats` as `int | None = None`; `to_config_lines` emits only the parts present.

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_parser.py`:

```python
class TestFeedbackShortForms:
    """The manufacturer documents omitting trailing sequence parameters."""

    def test_single_value_beep_is_parsed(self) -> None:
        """'TagBeep=100' is a single 100ms beep, not a parse failure."""
        from vtap100.parser import parse

        config = parse("!VTAPconfig\nTagBeep=100\n")
        assert config.feedback.beep.tag_beep is not None
        assert config.feedback.beep.tag_beep.on_ms == 100
        assert config.feedback.beep.tag_beep.off_ms is None

    def test_two_value_led_is_parsed(self) -> None:
        """'TagLED=00FF00,200' is the manufacturer's own example form."""
        from vtap100.parser import parse

        config = parse("!VTAPconfig\nTagLED=00FF00,200\n")
        assert config.feedback.led.tag_led is not None
        assert config.feedback.led.tag_led.color == "00FF00"
        assert config.feedback.led.tag_led.on_ms == 200

    def test_short_forms_roundtrip_as_short_forms(self) -> None:
        """A short form must not be expanded or dropped."""
        from vtap100.roundtrip import compare

        report = compare("!VTAPconfig\nTagBeep=100\nTagLED=00FF00,200\n")
        assert report.lost == []
        assert report.changed == []
```

- [ ] **Step 2: Add the fixture**

Create `tests/fixtures/valid_configs/feedback_short_forms.txt`:

```
!VTAPconfig

; The manufacturer documents omitting the interval and repeat count
; "for a single beep of the specified duration". Its own TagLED example
; is two-valued.
LEDSelect=1
LEDDefaultRGB=1EBBCF
PassLED=00FF00,200,1,1
TagLED=00FF00,200
PassBeep=100,100,2
TagBeep=100
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_parser.py::TestFeedbackShortForms -q`
Expected: FAIL — both sequences come back `None` because `_parse_beep_sequence` requires three parts.

- [ ] **Step 4: Make the trailing fields optional**

In `src/vtap100/models/feedback.py`:

```python
    off_ms: int | None = Field(default=None, ge=0, le=65535, description="Off time in ms")
    repeats: int | None = Field(default=None, ge=1, le=255, description="Number of repeats")
```

Apply to both `LEDSequence` and `BeepSequence`. In each `to_config_lines`, build the value from the parts that are set, stopping at the first `None`:

```python
        parts = [self.color, str(self.on_ms)]
        if self.off_ms is not None:
            parts.append(str(self.off_ms))
            if self.repeats is not None:
                parts.append(str(self.repeats))
        return ",".join(parts)
```

For `BeepSequence` the first part is `str(self.on_ms)` and `frequency` follows `repeats` on the same rule.

- [ ] **Step 5: Accept short forms in the parser**

In `src/vtap100/parser.py`, replace the length guard in `_parse_beep_sequence`:

```python
        parts = value.split(",")
        if not parts or not parts[0]:
            return None

        return BeepSequence(
            on_ms=int(parts[0]),
            off_ms=int(parts[1]) if len(parts) > 1 else None,
            repeats=int(parts[2]) if len(parts) > 2 else None,
            frequency=int(parts[3]) if len(parts) > 3 else None,
        )
```

Apply the same shape to `_parse_led_sequence`, where `parts[0]` is the colour and `on_ms` is `parts[1]`; require at least the colour and return `None` only when the value is empty.

- [ ] **Step 6: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add -A src tests
git commit -m "fix: accept LED and beep short forms

_parse_beep_sequence required at least three comma-separated parts and
returned None otherwise, silently discarding TagBeep=100 even though
the regex and model field both existed.

The manufacturer documents the short form explicitly, and its own
TagLED example is two-valued, so the tool was rejecting the vendor's
published syntax."
```

---

## Task 10: DESFire read length and offset keep explicit values

**Files:**
- Modify: `src/vtap100/models/desfire.py:56-57`

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_models_desfire.py`:

```python
class TestDESFireReadDefaults:
    """An explicitly set default value must keep its line."""

    def test_explicit_read_offset_zero_is_preserved(self) -> None:
        """ReadOffset=0 is also the default, and must not vanish."""
        from vtap100.roundtrip import compare

        report = compare("!VTAPconfig\nDESFire1AppID=AABBCC\nDESFire1ReadOffset=0\n")
        assert report.lost == []

    def test_explicit_read_length_three_is_preserved(self) -> None:
        """ReadLength=3 is also the default."""
        from vtap100.roundtrip import compare

        report = compare("!VTAPconfig\nDESFire1AppID=AABBCC\nDESFire1ReadLength=3\n")
        assert report.lost == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_models_desfire.py::TestDESFireReadDefaults -q`
Expected: FAIL — both lines are dropped because the value equals the model default.

- [ ] **Step 3: Make the fields optional**

```python
    read_length: int | None = Field(default=None, ge=1, le=255, description="Read length (1-255, reader default 3)")
    read_offset: int | None = Field(default=None, ge=0, le=255, description="Read offset (0-255, reader default 0)")
```

In `to_config_lines`, emit each only when not `None`.

- [ ] **Step 4: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS. Any test asserting `read_length == 3` on a default-constructed model must change to `is None`.

- [ ] **Step 5: Commit**

```bash
git add -A src tests
git commit -m "fix: preserve explicitly set DESFire read length and offset

A field whose default equals the value in the file cannot distinguish
'explicitly set' from 'absent', so the generator dropped the line. Same
class of defect as KBPostfix, same fix."
```

---

## Task 11: NFCType numeric aliases

**Files:**
- Modify: `src/vtap100/parser.py:166-168`
- Create: `tests/fixtures/valid_configs/nfc_numeric_aliases.txt`

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_parser.py`:

```python
class TestNFCTypeAliases:
    """The manufacturer documents '=U or =1', '=N or =2', '=B or =3'."""

    @pytest.mark.parametrize(("numeric", "letter"), [("1", "U"), ("2", "N"), ("3", "B")])
    def test_numeric_alias_parses_as_letter(self, numeric: str, letter: str) -> None:
        """Numeric spellings are accepted and normalise to the letter form."""
        from vtap100.parser import parse

        numeric_config = parse(f"!VTAPconfig\nNFCType4={numeric}\n")
        letter_config = parse(f"!VTAPconfig\nNFCType4={letter}\n")
        assert numeric_config.nfc.type4 == letter_config.nfc.type4

    def test_numeric_alias_roundtrips(self) -> None:
        """The alias counts as preserved even though the letter is emitted."""
        from vtap100.roundtrip import compare

        assert compare("!VTAPconfig\nNFCType2=1\n").is_lossless
```

- [ ] **Step 2: Add the fixture**

Create `tests/fixtures/valid_configs/nfc_numeric_aliases.txt`:

```
!VTAPconfig

; The manufacturer's own sample file uses the numeric spelling.
NFCType2=1
NFCType4=D
TagReadFormat=a
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_parser.py::TestNFCTypeAliases -q`
Expected: FAIL — the regex character class `[0UNBDP]` excludes the digits, so the line is silently ignored.

- [ ] **Step 4: Widen the regexes and normalise**

In `src/vtap100/parser.py`:

```python
    NFC_TYPE2 = re.compile(r"^NFCType2=([0123UNBDP])$")
    NFC_TYPE4 = re.compile(r"^NFCType4=([0123UNBDP])$")
    NFC_TYPE5 = re.compile(r"^NFCType5=([0123UNBDP])$")

    # Documented equivalent spellings: "=U or =1", "=N or =2", "=B or =3".
    NFC_TYPE_ALIASES = {"1": "U", "2": "N", "3": "B"}
```

At each of the three match sites, map the captured value before constructing the mode:

```python
            raw = match.group(1)
            value = self.NFC_TYPE_ALIASES.get(raw, raw)
```

- [ ] **Step 5: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS. The `roundtrip.NORMALISE` table added in Task 1 is what lets `NFCType2=1` count as preserved when `NFCType2=U` is written back.

- [ ] **Step 6: Commit**

```bash
git add -A src tests
git commit -m "fix: accept NFCType numeric aliases

The manufacturer documents '=U or =1', '=N or =2', '=B or =3' and uses
the numeric spelling in its own sample file. The character class
excluded the digits, so those lines were silently discarded."
```

---

## Task 12: Un-numbered DESFire spellings

Single-read configurations spell the settings without an index: `DESFireAppID` rather than `DESFire1AppID`. The parser recognises only the numbered form.

**Files:**
- Modify: `src/vtap100/parser.py:184-192` (DESFire regexes and their match sites)
- Create: `tests/fixtures/valid_configs/desfire_unnumbered.txt`

- [ ] **Step 1: Write the failing test**

Append to `tests/unit/test_parser.py`:

```python
class TestDESFireUnnumbered:
    """Single-read configs omit the index: DESFireAppID, not DESFire1AppID."""

    def test_unnumbered_maps_to_slot_one(self) -> None:
        """An un-numbered setting is the first DESFire read."""
        from vtap100.parser import parse

        config = parse("!VTAPconfig\nDESFireAppID=AABBCC\nDESFireFileID=0\n")
        assert config.desfire.apps[0].app_id == "AABBCC"
        assert config.desfire.apps[0].file_id == 0

    def test_unnumbered_diversification_is_parsed(self) -> None:
        """DESFireKeyDiversification is the un-numbered spelling."""
        from vtap100.parser import parse

        config = parse("!VTAPconfig\nDESFireAppID=AABBCC\nDESFireKeyDiversification=5\n")
        assert config.desfire.apps[0].diversification == 5
```

- [ ] **Step 2: Add the fixture**

Create `tests/fixtures/valid_configs/desfire_unnumbered.txt`:

```
!VTAPconfig

; Single-read spelling, without the index. The generator writes the
; numbered form back, which the round-trip comparison treats as equal
; through the alias table.
NFCType4=D
DESFireAppID=AABBCC
DESFireFileID=0
DESFireKeySlot=2
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_parser.py::TestDESFireUnnumbered -q`
Expected: FAIL — `config.desfire` is `None`, no app was recognised.

- [ ] **Step 4: Make the index optional**

In `src/vtap100/parser.py`, change each DESFire regex so the index may be absent, and treat a missing index as slot 1:

```python
    DESFIRE_APP_ID = re.compile(r"^DESFire(\d*)AppID=(.+)$")
    DESFIRE_FILE_ID = re.compile(r"^DESFire(\d*)FileID=(\d+)$")
    DESFIRE_KEY_SLOT = re.compile(r"^DESFire(\d*)KeySlot=(\d+)$")
    DESFIRE_DIVERSIFICATION = re.compile(r"^DESFire(\d*)(?:Key)?Diversification=(\d+)$")
```

Apply the same `(\d*)` change to the remaining `DESFire(\d+)` patterns. At every match site the slot is read as:

```python
            slot = int(match.group(1)) if match.group(1) else 1
```

The un-numbered spelling is a different **key**, not a different value, so
`NORMALISE` from Task 1 cannot express it — that table maps values. Add a
second, key-level table to `src/vtap100/roundtrip.py`:

```python
# Un-numbered DESFire settings are the single-read spelling of index 1.
KEY_ALIASES = {
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
```

and in `extract_settings`, `settings[KEY_ALIASES.get(key.strip(), key.strip())] = value.strip()`.

- [ ] **Step 5: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add -A src tests
git commit -m "fix: accept un-numbered DESFire settings

Single-read configurations spell these without an index. The parser
recognised only DESFire1AppID and silently ignored DESFireAppID.

Read-side alias only: the generator keeps writing the numbered form,
and the round-trip comparison maps the two spellings to one key."
```

---

## Task 13: Apple Access section

**Files:**
- Create: `src/vtap100/models/access.py`
- Modify: `src/vtap100/models/config.py`, `src/vtap100/parser.py`, `src/vtap100/generator.py`
- Create: `tests/unit/test_models_access.py`, `tests/fixtures/valid_configs/apple_access.txt`

**Interfaces:**
- Produces: `AccessConfig(tci: str | None, auth_required: bool | None, ecp2_mode: str | None)` with `to_config_lines() -> list[str]`; `VTAPConfig.access: AccessConfig | None`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_models_access.py`:

```python
"""Unit tests for Apple Access configuration."""

import pytest
from pydantic import ValidationError


class TestAccessConfig:
    """AccessTCI is a 3-byte hex value; AccessAuthRequired is 0/1."""

    def test_valid_tci(self) -> None:
        """A six-character hex TCI is accepted."""
        from vtap100.models.access import AccessConfig

        assert AccessConfig(tci="020000").tci == "020000"

    def test_tci_is_uppercased(self) -> None:
        """Hex is normalised to upper case."""
        from vtap100.models.access import AccessConfig

        assert AccessConfig(tci="02ab00").tci == "02AB00"

    def test_non_hex_tci_is_rejected(self) -> None:
        """A non-hex TCI is an error."""
        from vtap100.models.access import AccessConfig

        with pytest.raises(ValidationError):
            AccessConfig(tci="ZZZZZZ")

    def test_config_lines(self) -> None:
        """Only the fields that are set produce lines."""
        from vtap100.models.access import AccessConfig

        assert AccessConfig(tci="020000", auth_required=True).to_config_lines() == [
            "AccessTCI=020000",
            "AccessAuthRequired=1",
        ]


class TestAccessCoexistsWithVAS:
    """AccessTCI does not disable the pass sections."""

    def test_vas_smarttap_and_access_in_one_config(self) -> None:
        """All three ecosystems coexist in one running configuration."""
        from vtap100.parser import parse

        config = parse(
            "!VTAPconfig\n"
            "VAS2MerchantID=pass.com.example.x\n"
            "ST3CollectorID=12345678\n"
            "AccessTCI=020000\n"
        )
        assert len(config.vas_configs) == 1
        assert len(config.smarttap_configs) == 1
        assert config.access is not None
```

- [ ] **Step 2: Add the fixture**

Create `tests/fixtures/valid_configs/apple_access.txt`:

```
!VTAPconfig

; AccessTCI puts the reader in ECP2 mode. It does not disable VAS:
; the three ecosystems coexist in production configurations.
VAS2MerchantID=pass.com.example.library-card
VAS2KeySlot=2

NFCType4=D
DESFire1AppID=AABBCC
DESFire1FileID=0
DESFire1KeySlot=2

AccessTCI=020000
AccessAuthRequired=0
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run --extra dev pytest tests/unit/test_models_access.py -q`
Expected: FAIL — `No module named 'vtap100.models.access'`.

- [ ] **Step 4: Create the model**

Create `src/vtap100/models/access.py`:

```python
"""Apple Access (ECP2) configuration models.

Apple Access lets passes in Apple Wallet act as electronic keys. Setting
AccessTCI puts the reader in ECP2 mode and enables DESFire credential reading.
It does not disable Apple VAS: the two coexist in production configurations.

References:
    - https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Access-settings.htm
"""

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class AccessConfig(BaseModel):
    """Configuration for Access using Apple Wallet.

    Attributes:
        tci: Terminal Configuration Identifier, a 3-byte hex value assigned by
            Apple to the credential issuer.
        auth_required: Require device authentication on every tap.
        ecp2_mode: 't' for Apple Transit, 'a' for Apple Access.
    """

    tci: str | None = Field(default=None, description="Terminal Configuration Identifier (3-byte hex)")
    auth_required: bool | None = Field(default=None, description="Require authentication on every tap")
    ecp2_mode: str | None = Field(default=None, pattern="^[ta]$", description="ECP2 mode: t=Transit, a=Access")

    @field_validator("tci")
    @classmethod
    def validate_tci(cls, v: str | None) -> str | None:
        """Validate the TCI is hex of even length.

        The reader conventionally expects 3 bytes, but the exact length is not
        enforced so that valid TCIs of other lengths are not excluded.

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
        if not candidate or len(candidate) % 2 or not all(c in "0123456789ABCDEF" for c in candidate):
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
```

- [ ] **Step 5: Wire it in**

In `src/vtap100/models/config.py`, add the import and the field:

```python
    access: AccessConfig | None = Field(default=None, description="Apple Access (ECP2) configuration")
```

In `src/vtap100/parser.py`, add the three regexes, an `_AccessParseData` dataclass, a `_parse_access_line` branch, and construction in `_build_config` when any field is set:

```python
    ACCESS_TCI = re.compile(r"^AccessTCI=([0-9A-Fa-f]+)$")
    ACCESS_AUTH_REQUIRED = re.compile(r"^AccessAuthRequired=(\d+)$")
    ECP2_MODE = re.compile(r"^ECP2Mode=([ta])$")
```

In `src/vtap100/generator.py`, in `_generate_static_config_lines`, after the DESFire block:

```python
        # Apple Access
        if self.config.access:
            access_lines = self.config.access.to_config_lines()
            if access_lines:
                lines.append("; Apple Access (ECP2)")
                lines.extend(access_lines)
```

- [ ] **Step 6: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add -A src tests
git commit -m "feat: support Apple Access settings

AccessTCI, AccessAuthRequired and ECP2Mode had no regex, no model
field and no generator output, so they vanished from every
configuration that used them.

The fixture asserts what the manufacturer's wording obscures: setting
AccessTCI does not disable VAS. Production configurations run VAS,
Smart Tap and Access together."
```

---

## Task 14: ComPort section

**Files:**
- Create: `src/vtap100/models/comport.py`
- Modify: `src/vtap100/models/config.py`, `src/vtap100/parser.py`, `src/vtap100/generator.py`
- Create: `tests/unit/test_models_comport.py`

**Interfaces:**
- Produces: `ComPortConfig(enable: bool | None, mode: int | None, source: str | None)` with `to_config_lines()`; `VTAPConfig.com_port: ComPortConfig | None`. `source` uses the same bitmask as `KBSource`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_models_comport.py`:

```python
"""Unit tests for serial port configuration."""


class TestComPortConfig:
    """ComPortSource uses the same bitmask as KBSource."""

    def test_config_lines(self) -> None:
        """Only the fields that are set produce lines."""
        from vtap100.models.comport import ComPortConfig

        config = ComPortConfig(enable=False, mode=1, source="A1")
        assert config.to_config_lines() == [
            "ComPortEnable=0",
            "ComPortMode=1",
            "ComPortSource=A1",
        ]

    def test_source_accepts_kbsource_builder_output(self) -> None:
        """The bitmask is shared, so the builder applies unchanged."""
        from vtap100.models.comport import ComPortConfig
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().mobile_pass().card_tag_uid().build()
        assert ComPortConfig(source=source).source == "81"

    def test_roundtrip(self) -> None:
        """Serial settings survive a cycle."""
        from vtap100.roundtrip import compare

        text = "!VTAPconfig\nComPortEnable=0\nComPortMode=1\nComPortSource=A1\n"
        assert compare(text).is_lossless
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run --extra dev pytest tests/unit/test_models_comport.py -q`
Expected: FAIL — `No module named 'vtap100.models.comport'`.

- [ ] **Step 3: Create the model and wire it in**

Create `src/vtap100/models/comport.py` following the shape of `access.py`: a `ComPortConfig` with `enable: bool | None`, `mode: int | None` (`ge=0`), `source: str | None`, a `to_config_lines()` emitting only set fields, and a module docstring pointing at the keyboard settings page since the bitmask is shared with `KBSource`. Do not restate the bit meanings — reference `KBSourceBuilder`.

Add `com_port` to `VTAPConfig`, three regexes and a parse branch to `parser.py`, and a generator section titled `; Serial Port`.

- [ ] **Step 4: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A src tests
git commit -m "feat: support serial port settings

ComPortEnable, ComPortMode and ComPortSource appear in the
manufacturer's sample configuration and were dropped entirely.

ComPortSource carries the same bitmask as KBSource, so it reuses
KBSourceBuilder rather than restating the eight bit meanings."
```

---

## Task 15: The real-world corpus

The payoff. Four anonymised shapes plus the manufacturer's published example, all round-tripping losslessly.

**Files:**
- Create: `tests/fixtures/valid_configs/vendor_sample.txt`, `full_vas_st_desfire.txt`, `single_slot_all.txt`, `access_no_vas.txt`, `passes_only.txt`

**Interfaces:** none — these are data files consumed by the Task 2 battery.

- [ ] **Step 1: Add the manufacturer's sample**

Fetch `https://www.vtapnfc.com/downloads/config.txt` and save it verbatim as `tests/fixtures/valid_configs/vendor_sample.txt`, prefixing a provenance comment immediately after the `!VTAPconfig` header:

```
; Source: https://www.vtapnfc.com/downloads/config.txt
; Retrieved 2026-08-29. Contains no deployment data.
; This file loses 11 of its 19 settings before this work.
```

- [ ] **Step 2: Run the battery to see where it stands**

Run: `uv run --extra dev pytest tests/integration/test_fixture_configs.py -q -k vendor_sample`
Expected: PASS. If anything is still reported lost, that setting is a gap Tasks 3-14 did not close — fix it before continuing rather than excluding the file.

- [ ] **Step 3: Add the four anonymised shapes**

The 17 real configurations reduce to four shapes. Each fixture below is a real deployment file with only the identifiers replaced — structure, ordering, blank lines and comments are preserved byte for byte, including quirks such as the commented-out KB lines and the double blank line in shape B. Do not tidy them up: the point is to test what readers actually emit.

`full_vas_st_desfire.txt` — shape A, VAS + Smart Tap + DESFire + Access across pass slots 2 and 3:

```
!VTAPconfig

; This CONFIG.TXT was generated by a provisioning tool. Edit it to suit
; your deployment. Refer to the documentation at vtapnfc.com for the full
; reference. Copy private1.pem .. private6.pem onto the VTAP100 and reboot;
; the key is loaded into the reader at start-up and the file deleted
; automatically.

TagReadFormat=a

KBLogMode=1
KBSource=81
KBDelayMS=2
KBPassMode=0
;KBPassSection=2
;KBPassStart=0
;KBPassLength=14

LEDSelect=1
LEDDefaultRGB=1EBBCF

PassBeep=100,100,2
TagBeep=100

PassLED=00FF00,200,1,1
TagLED=00FF00,200

KBPostfix=%0D

VAS2MerchantID=pass.com.example.library-card
VAS2KeySlot=2

ST3CollectorID=12345678
ST3KeySlot=3
ST3KeyVersion=1

; VTAP100 DESFire config (Read-Only Reader)
; Profile: desfire_example_v1
; AIDs: 1 (aabbcc) / 1 files
; Diversification: 1 (UID + AID)
; SysID: 4558414D504C455F7379735F31303030 (16B)

NFCType4=D

DESFire1AppID=AABBCC
DESFire1FileID=0
DESFire1Crypto=3
DESFire1KeyNum=2
DESFire1KeySlot=2
DESFire1Format=0
DESFire1ReadLength=236

DESFire1Diversification=1
DESFire1PrivacyKeyNum=0
DESFire1PrivacyKeySlot=1
DESFire1SysIDKeySlot=3
DESFire1SysIDLength=16

AccessTCI=030000
```

`single_slot_all.txt` — shape B, all three ecosystems with everything in pass slot 2. Derived from a real deployment file. Note the double blank line before the DESFire comment block: the generator that produced it embeds a fragment, and the fixture keeps that quirk because a round-trip must survive it:

```
!VTAPconfig

; This CONFIG.TXT was generated by a provisioning tool. Edit it to suit your
; deployment. Refer to the documentation at vtapnfc.com for the full reference.
; Copy private1.pem .. private6.pem onto the VTAP100 and reboot; the key is
; loaded into the reader at start-up and the file deleted automatically.

TagReadFormat=a

KBLogMode=1
KBSource=81
KBDelayMS=2
KBPassMode=0
;KBPassSection=2
;KBPassStart=0
;KBPassLength=14

LEDSelect=1
LEDDefaultRGB=1EBBCF

PassBeep=100,100,2
TagBeep=100

PassLED=00FF00,200,1,1
TagLED=00FF00,200

KBPostfix=%0D

VAS2MerchantID=pass.com.example.library-card
VAS2KeySlot=2

ST2CollectorID=12345678
ST2KeySlot=2
ST2KeyVersion=1


; VTAP100 DESFire config (Read-Only Reader)
; Profile: desfire_example_v1
; AIDs: 1 (aabbcc) / 1 files
; Diversification: 1 (UID + AID)
; SysID: 4558414D504C455F7379735F31303030 (16B)

NFCType4=D

DESFire1AppID=AABBCC
DESFire1FileID=0
DESFire1Crypto=3
DESFire1KeyNum=2
DESFire1KeySlot=2
DESFire1Format=0
DESFire1ReadLength=236

DESFire1Diversification=1
DESFire1PrivacyKeyNum=0
DESFire1PrivacyKeySlot=1
DESFire1SysIDKeySlot=3
DESFire1SysIDLength=16

AccessTCI=020000
```

`access_no_vas.txt` — shape C, Smart Tap + DESFire + Apple Access with no VAS section. Derived from a real deployment file; this is the most common shape in the corpus. Its `AccessTCI` contains hex letters, which exercises the upper-casing in `AccessConfig.validate_tci` that an all-digit TCI would not:

```
!VTAPconfig

; This CONFIG.TXT was generated by a provisioning tool. Edit it to suit your
; deployment. Refer to the documentation at vtapnfc.com for the full reference.
; Copy private1.pem .. private6.pem onto the VTAP100 and reboot; the key is
; loaded into the reader at start-up and the file deleted automatically.

TagReadFormat=a

KBLogMode=1
KBSource=81
KBDelayMS=2
KBPassMode=0
;KBPassSection=2
;KBPassStart=0
;KBPassLength=14

LEDSelect=1
LEDDefaultRGB=1EBBCF

PassBeep=100,100,2
TagBeep=100

PassLED=00FF00,200,1,1
TagLED=00FF00,200

KBPostfix=%0D

ST2CollectorID=87654321
ST2KeySlot=2
ST2KeyVersion=1

; VTAP100 DESFire config (Read-Only Reader)
; Profile: desfire_example_v1
; AIDs: 1 (aabbcc) / 1 files
; Diversification: 1 (UID + AID)
; SysID: 4558414D504C455F7379735F31303030 (16B)

NFCType4=D

DESFire1AppID=AABBCC
DESFire1FileID=0
DESFire1Crypto=3
DESFire1KeyNum=2
DESFire1KeySlot=2
DESFire1Format=0
DESFire1ReadLength=236

DESFire1Diversification=1
DESFire1PrivacyKeyNum=0
DESFire1PrivacyKeySlot=1
DESFire1SysIDKeySlot=3
DESFire1SysIDLength=16

AccessTCI=02AB40
```

`passes_only.txt` — shape D, VAS + Smart Tap with no DESFire, Apple Access or NFC type section. Also derived from a real deployment file. Note that both pass sections sit in slot 2 and both point at key slot 2, so this fixture doubles as the proof that key slots are shared across sections:

```
!VTAPconfig

; This CONFIG.TXT was generated by a provisioning tool. Edit it to suit your
; deployment. Refer to the documentation at vtapnfc.com for the full reference.
; Copy private1.pem .. private6.pem onto the VTAP100 and reboot; the key is
; loaded into the reader at start-up and the file deleted automatically.

TagReadFormat=a

KBLogMode=1
KBSource=81
KBDelayMS=2
KBPassMode=0
;KBPassSection=2
;KBPassStart=0
;KBPassLength=14

LEDSelect=1
LEDDefaultRGB=1EBBCF

PassBeep=100,100,2
TagBeep=100

PassLED=00FF00,200,1,1
TagLED=00FF00,200

KBPostfix=%0D

VAS2MerchantID=pass.com.example.library-card
VAS2KeySlot=2

ST2CollectorID=12345678
ST2KeySlot=2
ST2KeyVersion=1
```

- [ ] **Step 4: Verify no key material or real identifiers leaked**

Run:
```bash
grep -rEi "BEGIN|h-da|ana-u|heidi|D011F1|f111d0|48454944|19091018|72603931|85401621|02A340" tests/fixtures/
```
Expected: no output. Any hit is a real identifier that must be replaced before committing.

- [ ] **Step 5: Run the full suite**

Run: `uv run --extra dev pytest -q`
Expected: PASS, with the fixture battery now covering roughly 15 configurations.

- [ ] **Step 6: Check coverage and quality gates**

Run: `uv run --extra dev pytest -q --cov --cov-report=term-missing | tail -20`
Expected: total coverage at or above 93%.

Run: `uv run --extra dev ruff check . && uv run --extra dev ruff format --check . && uv run --extra dev mypy src/`
Expected: all clean.

- [ ] **Step 7: Verify against the real corpus**

If `~/Downloads/vtap/` is available, confirm the work achieved its goal:

```bash
uv run --extra dev python - <<'EOF'
import glob, os
from pathlib import Path
from vtap100.roundtrip import compare
files = sorted(glob.glob(os.path.expanduser("~/Downloads/vtap/**/CONFIG.TXT"), recursive=True))
for f in files:
    name = os.path.relpath(f, os.path.expanduser("~/Downloads/vtap"))
    try:
        report = compare(Path(f).read_text())
        status = "OK" if report.is_lossless else f"LOSS {report.lost} {report.changed}"
    except Exception as e:
        status = f"FAIL {type(e).__name__}: {str(e).splitlines()[0]}"
    print(f"{status:12} {name}")
EOF
```

Expected: `OK` for all 17. Before this work, 14 failed to parse and the other three lost 7 settings each. Any remaining loss is a gap to fix, not to accept.

- [ ] **Step 8: Commit**

```bash
git add tests/fixtures
git commit -m "test: add the real-world fixture corpus

The manufacturer's published example plus one anonymised
representative of each of the four shapes found across 17 real
deployment configurations.

vendor_sample.txt is the clearest measure of this work: it lost 11 of
its 19 settings at the start and now round-trips unchanged."
```

---

## Verification

Part 1 is complete when:

1. Every fixture in `tests/fixtures/valid_configs/` passes all four battery checks.
2. `vendor_sample.txt` round-trips with zero loss.
3. All 17 configurations in `~/Downloads/vtap/` report `OK` under the Task 15 Step 7 script.
4. Dropping a new file into `valid_configs/` subjects it to the full battery with no change to any test file.
5. `uv run --extra dev pytest -q` passes with coverage at or above 93%.
6. `ruff check`, `ruff format --check` and `mypy src/` are clean.

## Deferred to later parts

- **Part 2 — tooling:** `vtap100 validate --roundtrip`, `vtap100 anonymize`, the git-ignored `tests/fixtures/local_configs/` corpus and its parametrisation.
- **Part 3 — surface and documentation:** TUI sections and form fields for Apple Access and ComPort, the `KBDelayMS` strict input bound, the ST1 warning in `validate`, all documentation files listed in spec section 5.7, and `CHANGELOG.md`.

Both parts belong on this same branch so the documentation ships with the code, per `CLAUDE.md`.
