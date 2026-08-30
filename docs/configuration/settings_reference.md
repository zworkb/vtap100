# Settings Reference

Quick reference for all VTAP100 config.txt parameters. For detailed usage, see the individual configuration guides.

## Apple VAS

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `VAS#MerchantID` | string | must start with `pass.` | required | Apple Pass Type ID |
| `VAS#KeySlot` | int | 0-6 | omitted | Private key slot; 0 or omitted selects the key automatically |
| `VAS#MerchantURL` | string | URL | - | Optional URL on pass presentation |
| `VASDefaultPassesEnabled` | string | 1-6 | 1,2,3,4,5,6 | Enabled pass slots |

*# = slot number 1-6*

## Google Smart Tap

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `ST#CollectorID` | string | numeric | required | Google Collector ID |
| `ST#KeySlot` | int | 0-6 | omitted | Private key slot; 0 or omitted is the documented default |
| `ST#KeyVersion` | int | 0-65535 | 0 | Key version (must match Google) |
| `STDefaultPassesEnabled` | string | 1-6 | 1,2,3,4,5,6 | Enabled pass slots |

*# = slot number 1-6*

## Keyboard Emulation

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `KBLogMode` | bool | 0/1 | 0 | Enable keyboard output |
| `KBEnable` | bool | 0/1 | 1 | Enable USB keyboard device |
| `KBSource` | string | see below | A5 | Data sources to output |
| `KBPrefix` | string | ASCII-hex | - | Prefix before data |
| `KBPostfix` | string | ASCII-hex | %0A | Suffix after data (newline) |
| `KBDelayMS` | int | 5-255 | 5 | Keystroke delay in ms. Parsing accepts 0-255: the manufacturer's own sample file uses 2 |
| `KBPassMode` | bool | 0/1 | 0 | Enable payload extraction |
| `KBPassSection` | int | 0-255 | 0 | Section to extract |
| `KBPassSeparator` | char | any | \| | Section separator |
| `KBPassStart` | int | 0-65535 | 0 | Extraction start position |
| `KBPassLength` | int | 0-255 | 0 | Extraction length (0=all) |

### KBSource Bitmask

KBSource uses hexadecimal bitmasks:

| Bit | Value | Source |
|-----|-------|--------|
| 7 | 0x80 | Mobile Pass (Apple VAS / Google Smart Tap) |
| 6 | 0x40 | STUID |
| 5 | 0x20 | Card Emulation |
| 2 | 0x04 | Scanners |
| 1 | 0x02 | Command Interface |
| 0 | 0x01 | Card/Tag UID |

Common values: `A5` (default), `81`, `80`, `01`

## NFC Tags

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `NFCType2` | enum | 0,U,N,B | - | Type 2 mode (NTAG, Ultralight) |
| `NFCType4` | enum | 0,U,N,B,D | - | Type 4 mode (DESFire, ISO14443-4) |
| `NFCType5` | enum | 0,U,N,B | - | Type 5 mode (ICODE, ISO15693) |
| `NFCReportReadError` | bool | 0/1 | 0 | Report error on read failure |
| `IgnoreRandomUID` | bool | 0/1 | 0 | Filter random Type 4 UIDs |
| `TagByteOrder` | bool | 0/1 | 0 | Reverse byte order |

### NFC Tag Modes

| Mode | Description |
|------|-------------|
| 0 | Disabled |
| U | UID only |
| N | NDEF records |
| B | Block data |
| D | DESFire (Type 4 only) |

### Tag Block Reading

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `TagReadBlockNum` | int | 0-255 | - | Block number |
| `TagReadKeySlot` | int | 1-9 | - | Auth key slot |
| `TagReadKeyType` | enum | A,B,C | - | MIFARE key type |
| `TagReadOffset` | int | 0-15 | 0 | Start byte in block |
| `TagReadLength` | int | 1-16 | - | Bytes to read |
| `TagReadFormat` | enum | a,d,h | - | Output: ASCII/decimal/hex |
| `TagReadMinDigits` | int/A | 1-20 or A | - | Min UID digits (A=auto) |

## DESFire

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `DESFire#AppID` | string | 6 hex | required | Application ID |
| `DESFire#FileID` | int | 0-255 | - | File ID. File 0 is legal and common |
| `DESFire#KeyNum` | int | 0-15 | - | Key number |
| `DESFire#KeySlot` | int | 1-9 | - | Key slot |
| `DESFire#Crypto` | enum | 0,1,3 | - | 0=none, 1=3DES, 3=AES |
| `DESFire#Format` | enum | 0,1,2 | - | 0=raw, 1=KEY-ID v1, 2=v2 |
| `DESFire#ReadLength` | int | 1-255 | 3 | Bytes to read |
| `DESFire#ReadOffset` | int | 0-255 | 0 | Start offset |
| `DESFire#Diversification` | int | 0,1,3,5,7 | - | Key diversification bit field, see below |
| `DESFire#PrivacyKeyNum` | int | 0-15 | - | Privacy key number |
| `DESFire#PrivacyKeySlot` | int | 1-9 | - | Privacy key slot |
| `DESFire#SysIDKeySlot` | int | 0-9 | - | System ID key slot; 0 means no System Identifier |
| `DESFire#SysIDLength` | int | 0-16 | - | System ID length |
| `DESFireSeparator` | char | any | , | Multi-app separator |

### DESFire#Diversification Bit Field

`DESFire#Diversification` is a bit field, not an on/off switch:

| Bit | Value | Meaning |
|-----|-------|---------|
| 0 | 1 | AN10922 key diversification active |
| 1 | 2 | Omit the AID from the diversification input |
| 2 | 4 | Reverse UID byte order |

Only five combinations are meaningful, because bits 1 and 2 modify a feature
that bit 0 enables:

| Value | Behaviour |
|-------|-----------|
| `0` | No diversification |
| `1` | AN10922 over UID and AID (standard) |
| `3` | AN10922 over UID, without the AID |
| `5` | AN10922 with reversed UID byte order, AID included |
| `7` | AN10922 with reversed UID byte order, without the AID |

Values 2, 4 and 6 are rejected: they set a modifier without enabling
diversification.

The mode must match the provisioning system exactly. A wrong mode does not fail
loudly — the reader computes a different diversified key and authentication
simply stops working.

*# = slot number 1-9*

## LED

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `LEDMode` | enum | 0-3 | - | 0=off, 1=on, 2=status, 3=custom |
| `LEDSelect` | enum | 0-3 | - | 0=external, 1=compact, 2=square, 3=serial |
| `LEDDefaultRGB` | string | 6 hex | - | Default color (e.g., 00FF00) |
| `PassLED` | sequence | see below | - | Pass read LED |
| `TagLED` | sequence | see below | - | Tag read LED |
| `PassErrorLED` | sequence | see below | - | Error LED |
| `StartLED` | sequence | see below | - | Startup LED |

### LED Sequence Format

`RRGGBB,on_ms,off_ms,repeats`

Example: `00FF00,100,100,2` = green, 100ms on, 100ms off, 2 times

## Beep

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `PassBeep` | sequence | see below | - | Pass read beep |
| `TagBeep` | sequence | see below | - | Tag read beep |
| `PassErrorBeep` | sequence | see below | - | Error beep |
| `StartBeep` | sequence | see below | - | Startup beep |

### Beep Sequence Format

`on_ms,off_ms,repeats[,frequency]`

- Frequency: 100-20000 Hz (optional, default 3136)
- Example: `100,100,2,3136` = 100ms on, 100ms off, 2 times, 3136 Hz

## Config File Format

```ini
!VTAPconfig
; Comment
Parameter=Value
```

- Header `!VTAPconfig` required
- Comments start with `;`
- Parameters: `Name=Value`

## Apple Access (ECP2)

Setting `AccessTCI` puts the reader into ECP2 mode and enables DESFire
credential reading. It does **not** disable Apple VAS: a single reader can serve
Apple VAS, Google Smart Tap and Apple Access from one configuration file.

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `AccessTCI` | string | hex, whole bytes | - | Terminal Configuration Identifier assigned by Apple, conventionally 3 bytes |
| `AccessAuthRequired` | bool | 0/1 | 0 | Require device authentication on every tap |
| `ECP2Mode` | enum | t, a | a | `t` = Apple Transit, `a` = Apple Access |

## Serial Port

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `ComPortEnable` | bool | 0/1 | - | Enable serial port output |
| `ComPortMode` | int | 0+ | - | Serial output mode |
| `ComPortSource` | string | hex bitmask | - | Data sources for serial output |

`ComPortSource` uses the same bitmask as `KBSource`; see the KBSource section
above for the bit meanings.

## Manufacturer Documentation

The authority for every value range on this page. Where this project's
documentation disagreed with these, the manufacturer won.

- [Apple VAS settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-VAS_settings.htm)
- [Google Smart Tap settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-ST-settings.htm)
- [Keyboard/barcode emulation settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm)
- [NFC card or tag settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Card-Tag-settings.htm)
- [MIFARE DESFire settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-DESFire-settings.htm)
- [Access using Apple Wallet settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Access-settings.htm)
- [LED settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-LED-settings.htm)
