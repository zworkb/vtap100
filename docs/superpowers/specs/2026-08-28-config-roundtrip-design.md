# Spec: Lossless config.txt Round-Trip

Status: proposed
Date: 2026-08-28
Topic: real-world config fixtures, round-trip fidelity, spec-conform validation

## 1. Problem

`vtap100` cannot load a real VTAP100 `config.txt`, and when it can, saving the
file silently discards settings.

A configuration file taken from a live VTAP100 deployment (Apple VAS + Google
Smart Tap + MIFARE DESFire) fails to parse:

```
ValidationError for DESFireAppConfig
  file_id: Input should be greater than or equal to 1, input_value=0
```

After working around that single blocker, a load/save cycle over the same file
preserves **25 of 31 settings**. Eleven are dropped, five reappear under
different names.

The root cause is a validation and parser layer built from the repository's own
documentation rather than from the manufacturer specification. Every constraint
below was verified against `help.vtapnfc.com` (see section 9).

## 2. Evidence

Measured against the real-world file, not inferred.

### 2.1 Constraint defects

| Setting | Manufacturer | Model | Effect |
|---|---|---|---|
| `DESFire#FileID` | 0–255 | `ge=1` | file does not load |
| `DESFire#Diversification` | 0, 1, 3, 5, 7 | `bool` | 3/5/7 silently lost |
| `VAS#KeySlot` | 0–6, optional, 0=auto | required, `ge=1` | file does not load |
| `ST#KeySlot` | 0–6, optional, 0=default | required, `ge=1` | file does not load |
| `DESFire#KeyNum` | 0–15 | unchecked | invalid values accepted |
| `DESFire#SysIDKeySlot` | 0–9 | unchecked | invalid values accepted |
| `DESFire#PrivacyKeySlot` | 1–9 | unchecked | invalid values accepted |

`VAS#KeySlot` was made required by commit `f43eb0c`. The manufacturer states
"=0 or omitted (default), all available keys will be compared with the 4 byte
hash of the public key for the data, to choose the right key." The commit was a
regression; the pre-existing repository documentation was correct.

Diversification loss, reproduced:

```
in=1 -> model=True   -> out=['DESFire1Diversification=1']
in=3 -> model=False  -> out=[]
in=5 -> model=False  -> out=[]
in=7 -> model=False  -> out=[]
```

Values 3, 5 and 7 are documented NXP AN10922 variants (omit the AID from the
diversification calculation; reverse byte order). A user who loads such a file
and saves it gets a reader that no longer authenticates, with no warning.

### 2.2 Round-trip data loss

**Slot numbers are not preserved.** `VAS2*` becomes `VAS1*`, `ST3*` becomes
`ST2*`, and VAS and Smart Tap share a single counter. `AppleVASConfig` and
`GoogleSmartTapConfig` have no slot field at all, so the number is discarded at
parse time.

**Short forms are silently dropped.** `_parse_beep_sequence` requires at least
three comma-separated parts and returns `None` otherwise. `TagBeep=100` and
`TagLED=00FF00,200` are therefore lost, although the regex and the model field
both exist. The manufacturer documents short forms explicitly: "you can omit the
interval between beeps and number of repeats, for a single beep of the specified
duration", and the official `TagLED` example is two-valued (`=00FF00,500`).

**The keyboard parser covers 2 of 11 settings.** Only `KBLogMode` and `KBSource`
have regexes. `KBPostfix=%0D` is ignored, the model keeps its default `%0A`, and
on save the line disappears entirely — after which the reader emits LF instead
of CR. The model fields for all missing settings already exist; they were never
wired up.

**Apple Access is unsupported.** `AccessTCI`, `AccessAuthRequired` and
`ECP2Mode` have no regex, no model field and no generator output.

**`NFCType#` numeric aliases are rejected.** The manufacturer documents "=U or
=1", "=N or =2", "=B or =3". The regex accepts only `[0UNBDP]`, so `NFCType4=1`
is silently discarded.

### 2.3 Missing test infrastructure

The test suite reads no configuration file from disk. All 92 config snippets
across 12 test files are inline strings, and every one of them writes a
well-formed `KeySlot`. `tests/fixtures/` does not exist and never has, although
`tests/conftest.py` defines four fixtures pointing into it and three sample
dicts — seven fixtures, none of them used by any test. `tests/integration/`
contains only an `__init__.py`.

This is why the defects above went unnoticed: there is no corpus of real
configurations to test against.

## 3. Goals

1. A real VTAP100 configuration file loads without error.
2. A load/save cycle preserves every setting the file contains, byte-equivalent
   in value, and is idempotent.
3. Validation constraints match the manufacturer specification.
4. The test suite owns a fixture corpus of real configurations, and a test that
   fails when any setting is lost.

## 4. Non-goals

Out of scope, documented as known limitations in `docs/troubleshooting.md`:

- **Sequence references.** Firmware v5+ supports `TagBeep=100:tagbeep@beeps.ini`
  and `LEDDefaultRGB=FFFFFF:seq.comet@leds.ini`. Supporting these requires the
  LED and beep models to become a union of inline sequences and file references,
  plus a relationship to `leds.ini`/`beeps.ini`. Its own spec.
- **Bluetooth, OSDP, MIFARE Classic settings.** Untouched by this work.
- The `_help_content:` dead blocks and the `HelpLoader` exception swallowing
  identified in an earlier review. Unrelated to round-trip fidelity.

## 5. Design

### 5.1 Validation philosophy: tolerant read, strict create

Real files contain values outside the documented ranges. The flagship fixture
has `KBDelayMS=2`, below the documented minimum of 5, and the reader accepts it.

Therefore:

- **Parsing** accepts the full technically valid range and preserves the value
  verbatim. Loading a file never loses data because a value is unusual.
- **Creation** through the TUI and CLI constrains input to the documented range.
  Widgets carry the strict bounds; the model carries the tolerant ones.

This applies only where the two genuinely differ. `KBDelayMS` is the sole known
case: model `ge=0, le=255`, TUI input `min=5, max=255`. Everywhere else the
documented range is also the model range.

No warning infrastructure is introduced. Reporting spec deviations to the user
is a possible follow-up, not part of this work.

### 5.2 Fixture infrastructure

`tests/fixtures/` is created with the three subdirectories `tests/conftest.py`
already promises, making the four existing fixtures functional rather than
deleting them.

```
tests/fixtures/
├── valid_configs/                    # must parse without error
│   ├── full_vas_st_desfire.txt       # flagship: real deployment, anonymised
│   ├── vas_keyslot_omitted.txt       # KeySlot absent (manufacturer: valid)
│   ├── vas_keyslot_zero.txt          # KeySlot=0 (auto key selection)
│   ├── desfire_diversification.txt   # variants 0/1/3/5/7
│   ├── feedback_short_forms.txt      # TagBeep=100, TagLED=00FF00,200
│   ├── keyboard_full.txt             # all eleven KB settings
│   ├── nfc_numeric_aliases.txt       # NFCType4=1 etc.
│   ├── apple_access.txt              # AccessTCI, AccessAuthRequired, ECP2Mode
│   └── minimal.txt                   # header only
├── invalid_configs/                  # must fail with a specific field error
│   ├── desfire_fileid_256.txt
│   ├── desfire_keyslot_10.txt
│   ├── desfire_keynum_16.txt
│   ├── vas_keyslot_7.txt
│   └── vas_merchant_id_no_prefix.txt
└── expected_outputs/
    └── full_vas_st_desfire.txt       # canonical generator output
```

The flagship fixture preserves the structure, ordering, blank lines and comments
of the original file exactly. Only deployment identifiers are replaced:

| Original | Fixture |
|---|---|
| `pass.de.h-da.library-card` | `pass.com.example.library-card` |
| Collector ID `19091018` | `12345678` |
| AID `D011F1` | `AABBCC` |
| SysID `48454944495F7379735F313030303030` | `4558414D504C455F7379735F31303030` |
| Profile `desfire_ana-u_v1` | `desfire_example_v1` |

No key material enters the repository. The `.pem` and `appkey*.txt` files that
accompany a real deployment are not fixtures and never will be. `.gitignore`
gains `*.pem`, `*.key` and `appkey*.txt` as part of this work.

### 5.3 Test layers

**`tests/integration/test_fixture_configs.py`**, parametrised over every file in
`valid_configs/`:

| Test | Asserts |
|---|---|
| `test_parses_without_error` | the file loads |
| `test_roundtrip_preserves_all_settings` | every `Key=Value` of the input reappears with an equal value |
| `test_roundtrip_idempotent` | a second cycle changes nothing |
| `test_model_equality_after_roundtrip` | `parse(generate(parse(x))) == parse(x)` |

The comparison operates on `Key=Value` pairs, ignoring ordering, blank lines and
`;` comments, so commented-out lines such as `;KBPassStart=0` are excluded and
the generator stays free to reorder sections and emit its own comments.

**Documented aliases are compared after normalisation.** `NFCType4=1` and
`NFCType4=U` denote the same setting, and the generator emits the letter form.
Value equality is therefore evaluated through a small normalisation table —
currently the `NFCType#` aliases `1→U`, `2→N`, `3→B` — rather than by raw string
comparison. The table lives beside the test and contains only aliases the
manufacturer documents as equivalent. Every other setting is compared verbatim.
Idempotence is unaffected: the second cycle sees the already-normalised form.

`test_roundtrip_preserves_all_settings` is the test that would have caught every
defect in section 2.2. It is the centre of this work.

**`tests/integration/test_invalid_configs.py`**, parametrised over
`invalid_configs/`, asserts `ValidationError` naming the expected field — not
merely that some error occurred.

**Unit tests** stay in their existing locations: boundary values in
`test_models_desfire.py`, `test_models_vas.py`, `test_models_smarttap.py`,
`test_models_keyboard.py`; parser behaviour in `test_parser.py`.

Per the project's TDD rule, every test below is written and observed failing
before the corresponding implementation change.

### 5.4 Model changes

`src/vtap100/models/desfire.py`:

```python
file_id:          int | None = Field(default=None, ge=0, le=255)   # was ge=1
key_num:          int | None = Field(default=None, ge=0, le=15)    # was unchecked
sysid_key_slot:   int | None = Field(default=None, ge=0, le=9)     # was unchecked
privacy_key_slot: int | None = Field(default=None, ge=1, le=9)     # was unchecked
diversification:  int | None = Field(default=None)                 # was bool
    # validator: value in {0, 1, 3, 5, 7}
```

`src/vtap100/models/vas.py` and `smarttap.py`:

```python
slot:     int = Field(..., ge=1, le=6)                    # new
key_slot: int | None = Field(default=None, ge=0, le=6)    # was required, ge=1
```

**Absence must be representable.** A field whose type carries a non-`None`
default cannot distinguish "the file set this value explicitly" from "the file
said nothing". The generator then omits the line, and an explicitly set default
value is lost. `KBPostfix=%0A` is the obvious case, but the flagship fixture
already contains a second one: `KBPassMode=0`, where `0` is also the default.

Every optional setting therefore becomes `T | None = None`, with the documented
default applied at generation time rather than construction time. This affects
`src/vtap100/models/keyboard.py` — `enable`, `postfix`, `delay_ms`, `pass_mode`,
`pass_section`, `pass_separator`, `pass_start`, `pass_length` — and
`src/vtap100/models/desfire.py` — `read_length` (default 3) and `read_offset`
(default 0). `prefix` and `log_mode` are already optional or explicit and need
no change.

Consumers reading these attributes must handle `None`. The generator centralises
the defaults in one table so the documented values are stated once.

New model for Apple Access, following the existing per-section model pattern:
`AccessConfig` with `tci: str | None` (3-byte hex, validated),
`auth_required: bool | None`, `ecp2_mode: Literal["t", "a"] | None`, wired into
`VTAPConfig` as `access: AccessConfig | None`.

### 5.5 Parser and generator changes

- **Slot preservation.** The parser already captures the slot number in its
  regex group and discards it. It is passed into the model instead. The
  generator uses `config.slot` rather than `enumerate`, which also removes the
  shared VAS/Smart Tap counter.
- **Short forms.** `_parse_beep_sequence` accepts 1–4 parts, `_parse_led_sequence`
  2–4. Absent trailing fields stay `None` rather than voiding the whole
  sequence. `BeepSequence.off_ms` and `repeats` become optional. The generator
  emits only the parts that are present, so a short form round-trips as a short
  form.
- **Keyboard.** Nine new regexes and their wiring: `KBEnable`, `KBPrefix`,
  `KBPostfix`, `KBDelayMS`, `KBPassMode`, `KBPassSection`, `KBPassSeparator`,
  `KBPassStart`, `KBPassLength`. The generator emits every explicitly set value.
- **NFC aliases.** The `NFCType#` character class gains `1`, `2` and `3`,
  normalising to the existing letter values. The generator continues to emit the
  letter form.
- **Apple Access.** Three regexes, model wiring, generator section.
- **Jinja template.** `generator.py` line 33 and 40 emit
  `KeySlot={{ passinfo.slot }}`, which hardcodes key slot equal to pass slot.
  Corrected to `{{ passinfo.apple.key_slot }}` / `{{ passinfo.google.key_slot }}`.
  A test renders the template and asserts the emitted key slot.

### 5.6 TUI changes

`diversification` is currently a `Switch` in `forms/desfire.py`. With five valid
values it becomes a `Select`:

| Value | Label (EN) | Label (DE) |
|---|---|---|
| 0 | Off | Aus |
| 1 | AN10922 (UID + AID) | AN10922 (UID + AID) |
| 3 | Without AID | Ohne AID |
| 5 | Reversed byte order | Byte-Reihenfolge umgekehrt |
| 7 | Without AID, reversed | Ohne AID, umgekehrt |

New keyboard fields get form inputs in `forms/keyboard.py`; Apple Access gets a
new section, sidebar entry and form following the existing pattern. All labels
and help texts are added to `tui/help/{de,en}/*.yaml` and
`tui/i18n/translations/{de,en}.yaml`, per the project's bilingual UI rule.

`KBDelayMS` input carries `min=5, max=255` per section 5.1.

### 5.7 Documentation

Mandatory in the same branch, per `CLAUDE.md`:

- `docs/configuration/settings_reference.md` — corrected ranges, all keyboard
  settings, Apple Access section
- `docs/configuration/desfire.md` — FileID 0–255, Diversification 0/1/3/5/7
- `docs/configuration/apple_vas.md`, `google_smarttap.md` — KeySlot optional
- `docs/configuration/keyboard.md` — the nine newly supported settings
- `docs/configuration/led_beep.md` — short forms
- `docs/api.md` — the `0-6 (0=auto)` comments become correct again
- `docs/references/cli.md` and the tables in the `vtap100 docs` command
  (`cli.py` lines 575, 586) — currently state `0-6 (0=auto)` while the model
  enforces `1-6`
- `docs/references/sources.md` — the manufacturer pages cited in section 9 as
  the authority for every range
- `docs/troubleshooting.md` — the non-goals of section 4 as known limitations
- `CHANGELOG.md` — created; the breaking changes of section 6

### 5.8 `.gitignore`

`*.pem`, `*.key`, `appkey*.txt` and a case-insensitive `config.txt` pattern.
The repository is public and its subject matter is key slots; users will place
exactly these files beside the checkout.

## 6. Breaking changes

Two public API changes for library consumers:

- `DESFireAppConfig.diversification` changes from `bool | None` to `int | None`.
- `AppleVASConfig.key_slot` and `GoogleSmartTapConfig.key_slot` change from
  required to optional.
- `AppleVASConfig.slot` and `GoogleSmartTapConfig.slot` are new required fields.
- The keyboard and DESFire fields listed in section 5.4 become `T | None`, so
  attribute reads must handle `None` where they previously saw a default.

The package is `1.0.0b6` and classified `Development Status :: 3 - Alpha`, so
breaking changes are acceptable. They are recorded in the new `CHANGELOG.md`.

## 7. Verification

The work is complete when:

1. `uv run vtap100 editor tests/fixtures/valid_configs/full_vas_st_desfire.txt`
   opens the file.
2. `test_roundtrip_preserves_all_settings` passes for every valid fixture.
3. `pytest` passes with coverage at or above the existing 93% threshold.
4. `ruff check`, `ruff format --check` and `mypy src/` are clean.
5. Every documentation file in section 5.7 is updated.

## 8. Risks

- **Slot as a required field** changes construction of `AppleVASConfig` in
  existing tests and in `docs/api.md` examples. Mitigation: a default of 1 would
  hide bugs, so the field is required and all call sites are updated.
- **Optional `BeepSequence` fields** could let the generator emit incomplete
  sequences where a full one was intended. Mitigation: the generator emits
  exactly the parts that are set, and the idempotence test covers it.
- **The Apple Access section** enlarges the TUI surface. It is the smallest of
  the new sections (three fields) and follows the existing form pattern.

## 9. Sources

Every value range in this spec is quoted from the manufacturer documentation:

- [DESFire settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-DESFire-settings.htm)
  — FileID 0–255, KeyNum 0–15, Diversification 0/1/3/5/7, SysIDKeySlot 0–9,
  PrivacyKeySlot 1–9, SysIDLength 0–16, ReadLength 1–255
- [Apple VAS settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-VAS_settings.htm)
  — KeySlot "=1 to =6 … =0 or omitted (default)"
- [Google Smart Tap settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-ST-settings.htm)
  — KeySlot "=1 to =6, identifying key file. =0 or omitted (default)"
- [Keyboard/barcode emulation settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm)
  — all eleven KB settings with defaults; KBDelayMS "between 5ms and 255ms",
  KBPostfix default "=%0A", KBSource default "=A5"
- [LED settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-LED-settings.htm)
  — LED sequence format, two-valued TagLED example
- [Control the LEDs or buzzer](https://help.vtapnfc.com/en/Content/VTAP-Configuration-Guide/Control-the-LEDs-or-buzzer.htm)
  — "you can omit the interval between beeps and number of repeats, for a single
  beep of the specified duration"
- [Access using Apple Wallet settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Access-settings.htm)
  — AccessTCI 3-byte hex, AccessAuthRequired 0/1, ECP2Mode t/a
- [NFC card or tag settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Card-Tag-settings.htm)
  — TagReadFormat a/d/h, NFCType2/4/5 numeric aliases
