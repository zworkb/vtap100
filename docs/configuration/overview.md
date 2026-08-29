# config.txt Format

VTAP100 configuration is done via a `config.txt` file that is copied to the reader.

## File Format

### Header

Every valid configuration file must start with the header:

```
!VTAPconfig
```

### Comments

Comments are introduced with a semicolon:

```
; This is a comment
```

### Parameters

Parameters are specified in `Name=Value` format:

```
VAS1MerchantID=pass.com.example.test
VAS1KeySlot=1
```

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

; Keyboard Emulation
KBLogMode=1
KBSource=81
```

## Parameter Categories

### Apple VAS (Value Added Services)

| Parameter | Description | Values |
|-----------|-------------|--------|
| VAS#MerchantID | Apple Pass Type ID | `pass.com.*` |
| VAS#KeySlot | Private key slot | 0-6, optional (0 or omitted = automatic) |
| VAS#MerchantURL | Optional URL | URL string |

Up to 6 VAS configurations possible (VAS1 to VAS6).

### Google Smart Tap

| Parameter | Description | Values |
|-----------|-------------|--------|
| ST#CollectorID | Google Collector ID | String |
| ST#KeySlot | Private key slot | 0-6, optional (0 or omitted = default) |
| ST#KeyVersion | Key version | Integer |

Up to 6 Smart Tap configurations possible (ST1 to ST6).

### Keyboard Emulation

| Parameter | Description | Values |
|-----------|-------------|--------|
| KBLogMode | Enables keyboard output | 0, 1 |
| KBSource | Data sources | Hex string |
| KBEnable | Enable USB keyboard | 0, 1 |

### KBSource Values

KBSource uses hexadecimal bitmasks:

| Bit | Value | Source |
|-----|-------|--------|
| 7 | 0x80 | Mobile Pass (Apple VAS / Google Smart Tap) |
| 6 | 0x40 | STUID |
| 5 | 0x20 | Card Emulation |
| 2 | 0x04 | Scanners |
| 1 | 0x02 | Command Interface |
| 0 | 0x01 | Card/Tag UID |

Examples:
- `A5` = Mobile + Emulation + Scanners + UID (default)
- `81` = Mobile Pass + Card/Tag UID
- `80` = Mobile Pass only
- `01` = Card/Tag UID only

## Private Keys

Private keys are stored as PEM files in the root directory of the reader:

- `private1.pem` - Key slot 1
- `private2.pem` - Key slot 2
- ... up to `private6.pem`

Key slot 0 means automatic selection.

## See Also

- [Apple VAS Configuration](apple_vas.md)
- [Google Smart Tap Configuration](google_smarttap.md)
- [Keyboard Emulation](keyboard.md)
- [Upload to Reader](../deployment/upload_to_reader.md)
