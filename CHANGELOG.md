# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions are derived from git tags via `hatch-vcs`.

## [Unreleased]

Configuration files now survive a load/save cycle without losing settings.
Before this work, 14 of 17 real deployment configurations could not be loaded at
all, the remaining three lost 7 of their 17 settings each, and the
manufacturer's own published sample lost 11 of its 19.

### Fixed

- **`DESFire#FileID` accepts 0.** The manufacturer documents 0-255; the model
  required 1. File 0 is a legal DESFire file number and is what real
  deployments use, so this single constraint made most real configurations
  unloadable.
- **`VAS#KeySlot` and `ST#KeySlot` are optional again.** Both are documented as
  "=0 or omitted (default)". Making them required was a regression against the
  specification.
- **Pass slot numbers are preserved.** `VAS2` no longer becomes `VAS1`, and
  `ST3` no longer becomes `ST2`. `ST1` is written back as `ST1`: it does not
  work on real readers and new configurations still avoid it, but rewriting a
  slot read from a file is a silent change to the user's configuration.
- **`DESFire#Diversification` is a bit field, not a boolean.** Modes 3, 5 and 7
  were coerced to false and dropped on save. That failure is silent and severe:
  the reader computes a different diversified key and authentication stops
  working with nothing to indicate why.
- **All eleven keyboard settings are parsed.** Only `KBLogMode` and `KBSource`
  had ever been read. `KBPostfix=%0D` was silently replaced by the default
  `%0A` and then dropped, switching the reader from CR to LF.
- **LED and beep short forms are accepted.** `TagBeep=100` and
  `TagLED=00FF00,200` were discarded, although the manufacturer documents
  omitting trailing parameters and uses the short form in its own examples.
- **Explicitly set default values keep their line.** A file stating
  `KBPassMode=0` or `DESFire1ReadOffset=0` no longer loses it.
- **`NFCType#` numeric aliases are accepted.** `=1`, `=2` and `=3` are
  documented equivalents of `=U`, `=N` and `=B`, and appear in the
  manufacturer's own sample.
- **Un-numbered DESFire settings are accepted.** `DESFireAppID` is the
  single-read spelling of `DESFire1AppID`.
- **Documented ranges are enforced** for `DESFire#KeyNum` (0-15),
  `PrivacyKeyNum` (0-15), `PrivacyKeySlot` (1-9) and `SysIDKeySlot` (0-9).

### Added

- **Apple Access support**: `AccessTCI`, `AccessAuthRequired` and `ECP2Mode`.
  Setting `AccessTCI` puts the reader in ECP2 mode but does not disable Apple
  VAS — the two coexist in production configurations.
- **Serial port support**: `ComPortEnable`, `ComPortMode` and `ComPortSource`.
  `ComPortSource` shares the `KBSource` bitmask and reuses `KBSourceBuilder`.
- **`vtap100.roundtrip`**, the single definition of what "lossless" means,
  imported by both the test battery and (from the next release) the CLI.
- **A fixture corpus** under `tests/fixtures/`, parametrised by glob so a new
  configuration is covered without touching test code, plus a git-ignored
  `local_configs/` for testing against your own files.
- **A pre-commit hook** rejecting real deployment identifiers and key material
  in committed fixtures.

### Documented

- **Minimum firmware versions.** A VTAP reader silently ignores settings its
  firmware does not know — no error, nothing wrong with the file, and changing
  the value changes nothing. Diagnosed on a reader running v2.2.8.2 where
  `DESFire#ReadOffset` had no effect at any value, because that setting arrived
  in v2.3.0.2. `settings_reference.md` now carries a table of the settings this
  tool generates that need firmware newer than v2.2.4.0, `desfire.md` states the
  requirement where the setting is described, and `troubleshooting.md` explains
  how to recognise the symptom and read the version from `BOOT.TXT`.

### Changed — breaking

The package is `1.0.0b6` and classified `Development Status :: 3 - Alpha`.
Library consumers should note:

- `AppleVASConfig.slot` and `GoogleSmartTapConfig.slot` are **new required
  fields**. They are deliberately not defaulted: a default would silently
  reintroduce slot renumbering for models built in code.
- `AppleVASConfig.key_slot`, `GoogleSmartTapConfig.key_slot` and
  `GoogleSmartTapConfig.key_version` changed from required to optional.
- `DESFireAppConfig.diversification` changed from `bool | None` to `int | None`.
- Fields that previously carried the reader's defaults now carry `None` when the
  file does not set them, so attribute reads must handle `None`:
  `KeyboardConfig.enable`, `postfix`, `delay_ms`, `pass_mode`, `pass_section`,
  `pass_separator`, `pass_start`, `pass_length`; `DESFireAppConfig.read_length`
  and `read_offset`; `LEDSequence.off_ms`/`repeats` and
  `BeepSequence.off_ms`/`repeats`.

`KBDelayMS` parses as 0-255 rather than the documented 5-255. The
manufacturer's own sample file uses 2, so tolerance is what it takes to load the
vendor's reference configuration; the strict bound belongs on editor input.
