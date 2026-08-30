# MIFARE DESFire Configuration

The VTAP100 can read MIFARE DESFire cards and retrieve authenticated data.

## Basics

DESFire is a contactless smartcard type from NXP with encryption features. The VTAP100 supports up to 9 DESFire application configurations.

## Parameters

### DESFire#AppID

Application ID of the DESFire application (6 hex characters).

```ini
DESFire1AppID=AABBCC
DESFire2AppID=112233
```

### DESFire#FileID

File ID to read (0-255).

File 0 is a legal DESFire file number and is what real deployments use.

```ini
DESFire1FileID=0
```

### DESFire#KeyNum

Key number for authentication.

```ini
DESFire1KeyNum=0
```

### DESFire#KeySlot

Key slot for authentication (1-9).

```ini
DESFire1KeySlot=1
```

### DESFire#Crypto

Cryptographic mode.

```ini
DESFire1Crypto=0    ; No encryption
DESFire1Crypto=1    ; 3DES
DESFire1Crypto=3    ; AES
```

| Value | Mode |
|-------|------|
| 0 | No encryption |
| 1 | 3DES |
| 3 | AES |

### DESFire#Format

Data output format.

```ini
DESFire1Format=0    ; Raw data
DESFire1Format=1    ; KEY-ID v1
DESFire1Format=2    ; KEY-ID v2
```

| Value | Format |
|-------|--------|
| 0 | Raw data |
| 1 | KEY-ID v1 |
| 2 | KEY-ID v2 |

### DESFire#ReadLength

Number of bytes to read (1-255). Omitted means the reader's own default of 3.

```ini
DESFire1ReadLength=16
```

### DESFire#ReadOffset

> **Requires core firmware v2.3.0.2 or later.** Older firmware ignores this
> setting silently — no error, no warning, and the generated `config.txt` looks
> correct. Check your version in `BOOT.TXT` on the reader's mass storage.
> See [release notes](https://www.vtapnfc.com/downloads/VTAP_Release_Notes.pdf) and [Update firmware](https://help.vtapnfc.com/en/Content/VTAP-Configuration-Guide/Update-firmware.htm).

Start offset in file (0-255, default: 0).

```ini
DESFire1ReadOffset=4
```

### DESFire#Diversification

A bit field controlling which parts enter the AN10922 diversification input,
not a simple on/off switch.

| Bit | Value | Meaning |
|-----|-------|---------|
| 0 | 1 | AN10922 key diversification active |
| 1 | 2 | Omit the AID from the diversification input |
| 2 | 4 | Reverse UID byte order |

Only five combinations are meaningful, because bits 1 and 2 modify what bit 0
enables:

| Value | Behaviour |
|-------|-----------|
| `0` | No diversification |
| `1` | AN10922 over UID and AID (standard) |
| `3` | AN10922 over UID, without the AID |
| `5` | AN10922 with reversed UID byte order, AID included |
| `7` | AN10922 with reversed UID byte order, without the AID |

```ini
DESFire1Diversification=1    ; UID + AID, the usual setting
DESFire1Diversification=5    ; some NFC stacks deliver the UID LSB first
```

Values 2, 4 and 6 are rejected: they set a modifier without enabling
diversification.

The mode must match the provisioning system **exactly**. Choosing the wrong one
does not fail loudly — the reader computes a different diversified key, and
authentication simply stops working with nothing to indicate why.

### DESFireSeparator

Separator for multiple apps (default: `,`).

```ini
DESFireSeparator=;
```

## Python API

### Simple Configuration

```python
from vtap100.models.desfire import DESFireConfig, DESFireAppConfig

# Single DESFire app
app = DESFireAppConfig(
    app_id="AABBCC",
    file_id=1,
    key_slot=1,
)

config = DESFireConfig(apps=[app])
print(config.to_config_lines())
# ['DESFire1AppID=AABBCC', 'DESFire1FileID=1', 'DESFire1KeySlot=1']
```

### With Encryption

```python
from vtap100.models.desfire import (
    DESFireConfig,
    DESFireAppConfig,
    DESFireCryptoMode,
    DESFireDataFormat,
)

app = DESFireAppConfig(
    app_id="AABBCC",
    file_id=1,
    key_num=0,
    key_slot=1,
    crypto=DESFireCryptoMode.AES,
    format=DESFireDataFormat.KEYID_V1,
    read_length=16,
)

config = DESFireConfig(apps=[app])
print(config.to_config_lines())
# ['DESFire1AppID=AABBCC', 'DESFire1FileID=1', 'DESFire1KeyNum=0',
#  'DESFire1KeySlot=1', 'DESFire1Crypto=3', 'DESFire1Format=1',
#  'DESFire1ReadLength=16']
```

### Multiple Apps

```python
from vtap100.models.desfire import DESFireConfig, DESFireAppConfig

apps = [
    DESFireAppConfig(app_id="111111", file_id=1),
    DESFireAppConfig(app_id="222222", file_id=2),
    DESFireAppConfig(app_id="333333", file_id=3),
]

config = DESFireConfig(apps=apps, separator=";")
print(config.to_config_lines())
# ['DESFire1AppID=111111', 'DESFire1FileID=1',
#  'DESFire2AppID=222222', 'DESFire2FileID=2',
#  'DESFire3AppID=333333', 'DESFire3FileID=3',
#  'DESFireSeparator=;']
```

### Combined with VTAPConfig

```python
from vtap100.models.config import VTAPConfig
from vtap100.models.desfire import DESFireConfig, DESFireAppConfig, DESFireCryptoMode
from vtap100.models.keyboard import KeyboardConfig
from vtap100.generator import ConfigGenerator

# Combine DESFire + Keyboard
desfire = DESFireConfig(
    apps=[
        DESFireAppConfig(
            app_id="AABBCC",
            file_id=1,
            key_slot=1,
            crypto=DESFireCryptoMode.AES,
        )
    ]
)

kb = KeyboardConfig(
    log_mode=True,
    source="D1",  # DESFire App 1
)

config = VTAPConfig(desfire=desfire, keyboard=kb)

generator = ConfigGenerator(config)
print(generator.generate())
```

## Complete Example

```ini
!VTAPconfig
; MIFARE DESFire Settings
DESFire1AppID=AABBCC
DESFire1FileID=1
DESFire1KeyNum=0
DESFire1KeySlot=1
DESFire1Crypto=3
DESFire1ReadLength=16

; Keyboard Emulation
KBLogMode=1
KBSource=D1
```

## See Also

- [config.txt Format](overview.md)
- [Keyboard Emulation](keyboard.md)
- [NFC Tags](nfc_tags.md)

## Manufacturer Documentation

The authority for every value range on this page. Where this project's
documentation disagreed with these, the manufacturer won.

- [MIFARE DESFire and Apple Access settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-DESFire-settings.htm)
- [Access using Apple Wallet settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Access-settings.htm)
