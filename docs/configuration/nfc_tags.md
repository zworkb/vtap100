# NFC Tag Configuration

The VTAP100 can read various NFC tag types: Type 2, Type 4, and Type 5.

## Tag Types

### NFC Type 2

Typical tags: NTAG213/215/216, MIFARE Ultralight

```ini
NFCType2=U    ; Read UID
NFCType2=N    ; Read NDEF records
NFCType2=B    ; Read block data
NFCType2=0    ; Disabled (default)
```

### NFC Type 4

Typical tags: DESFire, ISO 14443-4 compatible

```ini
NFCType4=U    ; Read UID
NFCType4=N    ; Read NDEF records
NFCType4=B    ; Read block data
NFCType4=D    ; DESFire secure data
NFCType4=0    ; Disabled (default)
```

### NFC Type 5

Typical tags: ICODE, ISO 15693

```ini
NFCType5=U    ; Read UID
NFCType5=N    ; Read NDEF records
NFCType5=B    ; Read block data
NFCType5=0    ; Disabled (default)
```

## Read Modes

| Mode | Value | Description |
|------|-------|-------------|
| Disabled | 0 | Tag type disabled |
| UID | U | Read UID only |
| NDEF | N | Read NDEF records |
| Block | B | Read raw block data |
| DESFire | D | DESFire secure data (Type 4 only) |

## Additional Parameters

### NFCReportReadError

Output error payload on read errors.

```ini
NFCReportReadError=1    ; Report errors
NFCReportReadError=0    ; Ignore (default)
```

### IgnoreRandomUID

Filter random Type 4 UIDs (e.g., from smartphones).

```ini
IgnoreRandomUID=1    ; Ignore random UIDs
IgnoreRandomUID=0    ; Accept all UIDs (default)
```

### TagByteOrder

Reverse byte order.

```ini
TagByteOrder=1    ; Reverse bytes
TagByteOrder=0    ; Normal (default)
```

## Reading Block Data

For block mode (B) there are additional parameters:

### TagReadBlockNum

Block number to read (0-255).

```ini
TagReadBlockNum=4    ; Read block 4
```

### TagReadKeySlot

Key slot for authentication (1-9).

```ini
TagReadKeySlot=1    ; Use key from slot 1
```

### TagReadKeyType

Key type for MIFARE (A, B, or C).

```ini
TagReadKeyType=A    ; Key type A
TagReadKeyType=B    ; Key type B
```

### TagReadOffset

Start byte in block (0-15).

```ini
TagReadOffset=0     ; From beginning (default)
TagReadOffset=4     ; From byte 4
```

### TagReadLength

Number of bytes to read (1-16).

```ini
TagReadLength=4     ; Read 4 bytes
TagReadLength=16    ; Read entire block
```

### TagReadFormat

Output format.

```ini
TagReadFormat=h     ; Hexadecimal
TagReadFormat=d     ; Decimal
TagReadFormat=a     ; ASCII
```

### TagReadMinDigits

Minimum digits for UID output.

```ini
TagReadMinDigits=10    ; At least 10 digits
TagReadMinDigits=A     ; Automatic
```

## Python API

### Simple Configuration

```python
from vtap100.models.nfc import NFCTagConfig, NFCTagMode

# Enable Type 2 and Type 4 in UID mode
nfc = NFCTagConfig(
    type2=NFCTagMode.UID,
    type4=NFCTagMode.UID,
)

print(nfc.to_config_lines())
# ['NFCType2=U', 'NFCType4=U']
```

### Reading Block Data

```python
from vtap100.models.nfc import (
    NFCTagConfig, NFCTagMode,
    TagReadConfig, TagKeyType, TagReadFormat
)

# Read MIFARE block
tag_read = TagReadConfig(
    block_num=4,
    key_slot=1,
    key_type=TagKeyType.A,
    length=16,
    format=TagReadFormat.HEX,
)

nfc = NFCTagConfig(
    type2=NFCTagMode.BLOCK,
    tag_read=tag_read,
)

print(nfc.to_config_lines())
# ['NFCType2=B', 'TagReadBlockNum=4', 'TagReadKeySlot=1',
#  'TagReadKeyType=A', 'TagReadLength=16', 'TagReadFormat=h']
```

### Combined with VTAPConfig

```python
from vtap100.models.config import VTAPConfig
from vtap100.models.nfc import NFCTagConfig, NFCTagMode
from vtap100.models.keyboard import KeyboardConfig
from vtap100.generator import ConfigGenerator

# Combine NFC + Keyboard
nfc = NFCTagConfig(
    type2=NFCTagMode.UID,
    type4=NFCTagMode.NDEF,
    ignore_random_uid=True,
)

kb = KeyboardConfig(
    log_mode=True,
    source="24",  # Type 2 and Type 4
)

config = VTAPConfig(nfc=nfc, keyboard=kb)

generator = ConfigGenerator(config)
print(generator.generate())
```

## Complete Example

```ini
!VTAPconfig
; NFC Tag Settings
NFCType2=U
NFCType4=N
IgnoreRandomUID=1

; Keyboard Emulation
KBLogMode=1
KBSource=24
```

## See Also

- [config.txt Format](overview.md)
- [Keyboard Emulation](keyboard.md)
- [MIFARE DESFire](desfire.md) *(Phase 4)*

## Manufacturer Documentation

The authority for every value range on this page. Where this project's
documentation disagreed with these, the manufacturer won.

- [NFC card or tag settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Card-Tag-settings.htm)
