# CLI Reference

## Commands

```
vtap100 [--version] [--help] COMMAND
```

| Command | Description |
|---------|-------------|
| `generate` | Generate config.txt from CLI options |
| `wizard` | Interactive configuration wizard |
| `editor` | Visual TUI editor |
| `validate` | Validate existing config.txt |
| `docs` | Show parameter documentation |

## generate

Generate a config.txt file from command-line options.

```
vtap100 generate [OPTIONS]
```

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--apple-vas` | `-a` | TEXT | Apple VAS Merchant ID |
| `--google-st` | `-g` | TEXT | Google Collector ID |
| `--key-slot` | `-k` | 0-6 | Key slot; 0 lets the reader select the key automatically |
| `--key-version` | | INT | Google key version |
| `--keyboard` | | flag | Enable keyboard emulation |
| `--no-keyboard` | | flag | Disable keyboard emulation |
| `--output` | `-o` | FILE | Output file path |
| `--comment` | `-c` | TEXT | Add comment |

### Examples

```bash
# Apple VAS
vtap100 generate -a pass.com.example.myapp -k 1

# Google Smart Tap
vtap100 generate -g 96972794 -k 2 --key-version 1

# Combined with output file
vtap100 generate -a pass.com.example.myapp -g 96972794 -k 1 -o config.txt

# With keyboard enabled
vtap100 generate -a pass.com.example.myapp -k 1 --keyboard
```

## wizard

Interactive step-by-step configuration wizard. Supports all features.

```
vtap100 wizard
```

No options. Guides through:
- Apple VAS
- Google Smart Tap
- NFC Tags
- DESFire
- Keyboard Emulation
- LED/Beep Feedback

## editor

Visual TUI editor with live preview and context help.

```
vtap100 editor [OPTIONS] [FILENAME]
```

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--output` | `-o` | PATH | Output file |

### Examples

```bash
# New configuration
vtap100 editor

# Open existing file
vtap100 editor config.txt

# Specify output
vtap100 editor -o output.txt
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+S` | Save |
| `Ctrl+E` | Export |
| `Ctrl+O` | Open |
| `Ctrl+D` | Toggle docs |
| `Ctrl+L` | Toggle language |
| `Ctrl+Q` | Quit |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |

## validate

Validate an existing config.txt file.

```
vtap100 validate CONFIG_FILE
```

### Example

```bash
vtap100 validate /media/user/VTAP100/config.txt
```

## docs

Show inline parameter documentation.

```
vtap100 docs
```

Displays parameter tables for all configuration options.
