# Keyboard Emulation

Keyboard emulation allows the VTAP100 to send NFC data as keyboard input.

## How It Works

When enabled, the VTAP100 acts as a USB keyboard and automatically "types" the read data. This is useful for:

- POS systems without NFC API
- Legacy applications
- Quick integration without programming

## Parameters

### KBLogMode

Enables or disables keyboard emulation.

```ini
KBLogMode=1    ; Enabled
KBLogMode=0    ; Disabled
```

### KBSource

Defines which data sources trigger keyboard output. The value is a **hexadecimal bitmask**.

**Bit masks:**

| Bit | Hex Value | Source |
|-----|-----------|--------|
| 7 | 0x80 | Mobile Pass (Apple VAS / Google Smart Tap) |
| 6 | 0x40 | STUID |
| 5 | 0x20 | Card Emulation Write Mode |
| 2 | 0x04 | Scanners |
| 1 | 0x02 | Command Interface Messages |
| 0 | 0x01 | Card/Tag UID |

**Common values:**

| Value | Description |
|-------|-------------|
| A5 | Mobile Pass + Card Emulation + Scanners + UID (default) |
| 81 | Mobile Pass + Card/Tag UID |
| 80 | Mobile Pass only |
| 01 | Card/Tag UID only |

**Examples:**
```ini
KBSource=A5     ; Default: Mobile passes, card emulation, scanners, UID
KBSource=80     ; Mobile passes only (Apple VAS / Google Smart Tap)
KBSource=81     ; Mobile passes + Card/Tag UID
KBSource=01     ; Card/Tag UID only
KBSource=E7     ; All sources enabled (0x80+0x40+0x20+0x04+0x02+0x01)
```

### KBEnable

Enables or disables the USB keyboard device.

```ini
KBEnable=1    ; USB keyboard enabled
KBEnable=0    ; USB keyboard disabled
```

### KBPrefix

Optional: Output prefix before the data.

```ini
KBPrefix=$t$n:       ; Pass type and slot, e.g. "A22:"
KBPrefix=%0A         ; Newline as prefix
KBPrefix=ID:         ; Fixed text as prefix
```

**Substitution tokens** ([manufacturer documentation](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm)):

| Token | Expands to |
|-------|------------|
| `$t` | Pass type character — see the table below |
| `$n` | Merchant/collector index digit (1-6) and key slot digit (1-6). Used together as `$t$n` |
| `$u` | UID as 8, 14 or 16 hex ASCII digits |
| `$s` | VTAP serial number |
| `$$t` | A literal `$t`, not substituted |
| `%XX` | ASCII hex character, e.g. `%0A` = newline |

**Pass type characters** for `$t` ([manufacturer documentation](https://help.vtapnfc.com/en/Content/VTAP-Commands/Dynamic-config-commands.htm)):

| Character | Source |
|-----------|--------|
| `A` | Apple VAS pass |
| `G` | Google Smart Tap pass |
| `S` | Samsung VAS pass |
| `X` | Apple Access / ECP2 on iPhone |
| `W` | Apple Access / ECP2 on Apple Watch |
| `0` / `2` / `4` / `6` | MIFARE / NFC type 2 / type 4 / type 5 card or tag |
| `E` | Card emulation |
| `H` / `M` | mDL handover / mDL data |
| `Q` | Scanner input |

`$t` matters more than it looks: `KBPrefix`, `KBPostfix` and the payload
extraction settings are **global**, so there is no way to define a different
output format per source. Emitting the pass type and letting the receiving
system branch on it is the only mechanism the reader offers for distinguishing
Apple VAS from Google Smart Tap from Apple Access in the output.

### KBPostfix

Suffix after the data (default: `%0A` = newline).

```ini
KBPostfix=%0A        ; Newline (default)
KBPostfix=%0D%0A     ; CRLF (Windows)
KBPostfix=%09        ; Tab
```

### KBDelayMS

> The manufacturer documents 5-255 ms, but ships a sample `config.txt` using
> `KBDelayMS=2`. This tool therefore accepts 0-255 when reading a file, so such
> configurations load unchanged, while the editor constrains new input to the
> documented range.

Delay between keystrokes in milliseconds (5-255).

```ini
KBDelayMS=5          ; Fast (default)
KBDelayMS=50         ; Slower for older systems
KBDelayMS=100        ; Very slow
```

### KBPassMode

Enables extraction from the pass payload.

```ini
KBPassMode=1         ; Extraction enabled
KBPassMode=0         ; Disabled (default)
```

### KBPassSection

Which section from the payload is extracted (when PassMode is enabled).

```ini
KBPassSection=0      ; First section (default)
KBPassSection=1      ; Second section
KBPassSection=2      ; Third section
```

### KBPassSeparator

Separator between sections in the payload.

```ini
KBPassSeparator=|    ; Pipe (default)
KBPassSeparator=;    ; Semicolon
KBPassSeparator=,    ; Comma
```

### KBPassStart / KBPassLength

Start position and length of extraction.

```ini
KBPassStart=0        ; From beginning (default)
KBPassStart=10       ; From position 10

KBPassLength=0       ; All (default)
KBPassLength=16      ; Only 16 characters
```

## CLI Usage

```bash
# With keyboard emulation (default)
vtap100 generate --apple-vas pass.com.example.test --keyboard

# Without keyboard emulation
vtap100 generate --apple-vas pass.com.example.test --no-keyboard
```

## Python API

### Simple Configuration

```python
from vtap100.models.keyboard import KeyboardConfig

kb = KeyboardConfig(
    log_mode=True,
    source="A5",
    enable=True
)

print(kb.to_config_lines())
# ['KBLogMode=1', 'KBSource=A5']
```

### Extended Configuration

```python
from vtap100.models.keyboard import KeyboardConfig

kb = KeyboardConfig(
    log_mode=True,
    source="81",            # Mobile Pass + UID
    prefix="$t$n:",         # Pass type and slot, e.g. "A22:"
    postfix="%0D%0A",       # CRLF instead of LF
    delay_ms=50,            # Slower output
    pass_mode=True,         # Payload extraction
    pass_section=1,         # Second section
    pass_separator=";",     # Semicolon separation
    pass_length=32,         # Max 32 characters
)

print(kb.to_config_lines())
# ['KBLogMode=1', 'KBSource=81', 'KBPrefix=$t:', 'KBPostfix=%0D%0A',
#  'KBDelayMS=50', 'KBPassMode=1', 'KBPassSection=1',
#  'KBPassSeparator=;', 'KBPassLength=32']
```

### KBSource Builder

For constructing hex bitmask values there is a fluent builder:

```python
from vtap100.models.keyboard import KBSourceBuilder

# Mobile Pass + Card/Tag UID
source = (KBSourceBuilder()
    .mobile_pass()
    .card_tag_uid()
    .build())

print(source)  # "81"

# Default A5 configuration
source = (KBSourceBuilder()
    .mobile_pass()
    .card_emulation()
    .scanners()
    .card_tag_uid()
    .build())

print(source)  # "A5"
```

### Builder Methods

**Data sources (each sets a bit):**
- `.mobile_pass()` - Bit 7 (0x80): Apple VAS / Google Smart Tap
- `.stuid()` - Bit 6 (0x40): STUID
- `.card_emulation()` - Bit 5 (0x20): Card Emulation Write Mode
- `.scanners()` - Bit 2 (0x04): Scanners
- `.command_interface()` - Bit 1 (0x02): Command Interface Messages
- `.card_tag_uid()` - Bit 0 (0x01): Card/Tag UID

## Complete Example

```ini
!VTAPconfig
; Apple VAS Configuration
VAS1MerchantID=pass.com.example.myapp
VAS1KeySlot=1

; Google Smart Tap Configuration
ST1CollectorID=96972794
ST1KeySlot=2
ST1KeyVersion=1

; Keyboard Emulation - Mobile passes + UID
KBLogMode=1
KBSource=81
KBEnable=1
```

## Output Format

Data is output as a hex string, followed by Enter:

```
A1B2C3D4E5F6<Enter>
```

## Use Case Examples

### Mobile Pass Only

```ini
; Only mobile passes (Apple VAS / Google Smart Tap)
KBLogMode=1
KBSource=80
```

### Full Integration

```ini
; Mobile passes + Card emulation + UID (common setup)
KBLogMode=1
KBSource=A1
```

### UID-based Access Control

```ini
; Output only Card/Tag UID
KBLogMode=1
KBSource=01
```

## Tips

1. **Test first with `01`** - The Card/Tag UID is always available
2. **For mobile passes**: Use `80` or `81` (mobile passes, optionally with UID)
3. **Default `A5`**: Covers most use cases (mobile + emulation + scanners + UID)

## See Also

- [config.txt Format](overview.md)
- [Apple VAS Configuration](apple_vas.md)
- [Google Smart Tap Configuration](google_smarttap.md)

## Manufacturer Documentation

The authority for every value range on this page. Where this project's
documentation disagreed with these, the manufacturer won.

- [Keyboard/barcode emulation settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm)
- [Pass type characters](https://help.vtapnfc.com/en/Content/VTAP-Commands/Dynamic-config-commands.htm)
