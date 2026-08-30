# Google Smart Tap Configuration

Google Smart Tap enables reading Google Wallet passes via NFC.

## Prerequisites

1. A Google Pay & Wallet Console account
2. A Collector ID (provided by Google)
3. An ECDSA key pair for authentication
4. The public key must be registered with Google

## Parameters

> **Warning:** The first Smart Tap configuration slot (ST1) does not work. Always use ST2 and higher.

### ST#CollectorID

The Collector ID assigned by Google.

```ini
ST2CollectorID=96972794
```

### ST#KeySlot

The slot (1-6) where the private key is stored. Optional.

```ini
ST2KeySlot=1
```

The value 0, or omitting the setting entirely, is the documented default.

### ST#KeyVersion

The version number of the key being used.

```ini
ST2KeyVersion=1
```

## Complete Example

```ini
!VTAPconfig
; Google Smart Tap Configuration
; Note: ST1 does not work, always start with ST2
ST2CollectorID=96972794
ST2KeySlot=1
ST2KeyVersion=1

; Keyboard Emulation for Smart Tap data
KBLogMode=1
KBSource=G2
```

## CLI Usage

### Simple Configuration

```bash
vtap100 generate --google-st 96972794 --key-slot 2 --key-version 1
```

### Combined with Apple VAS

```bash
vtap100 generate \
    --google-st 96972794 \
    --apple-vas pass.com.example.myapp \
    --key-slot 1
```

### Interactive Wizard

```bash
vtap100 wizard
```

## Python API

```python
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.models.config import VTAPConfig
from vtap100.generator import ConfigGenerator

# Create Smart Tap configuration
st = GoogleSmartTapConfig(
    collector_id="96972794",
    key_slot=2,
    key_version=1
)

# Complete configuration
config = VTAPConfig(smarttap_configs=[st])

# Generate config.txt
generator = ConfigGenerator(config)
print(generator.generate())
```

## Multiple Collector IDs

Up to 5 different Collector IDs can be configured (ST2-ST6, since ST1 does not work):

```ini
!VTAPconfig
ST2CollectorID=96972794
ST2KeySlot=1
ST2KeyVersion=1

ST3CollectorID=12345678
ST3KeySlot=2
ST3KeyVersion=1
```

## Reading Smart Tap Data

With keyboard emulation enabled, Smart Tap data is automatically output:

```ini
KBLogMode=1
KBSource=G5    ; All bytes from Google Smart Tap
```

## Default Passes

In addition to custom Collector IDs, default passes can be enabled:

```python
from vtap100.models.smarttap import SmartTapDefaultPassesConfig

defaults = SmartTapDefaultPassesConfig(
    loyalty=True,      # Loyalty cards
    gift_card=True,    # Gift cards
    offer=True,        # Offers
    transit=False,     # Public transit
    event_ticket=True, # Event tickets
    flight=True,       # Flight tickets
    boarding=True      # Boarding passes
)
```

## Troubleshooting

### Smart Tap not working at all

- **ST1 configuration does not work** - always use ST2 and higher
- Ensure your config uses ST2CollectorID, ST2KeySlot, ST2KeyVersion (not ST1*)

### "No Smart Tap data received"

- Check the Collector ID
- Ensure the private key is in the correct slot
- Verify the key version matches

### "Authentication failed"

- The public key may not be registered with Google
- The key version doesn't match

## See Also

- [config.txt Format](overview.md)
- [Apple VAS Configuration](apple_vas.md)
- [Keyboard Emulation](keyboard.md)
- [Reference Sources](../references/sources.md)

## Manufacturer Documentation

The authority for every value range on this page. Where this project's
documentation disagreed with these, the manufacturer won.

- [Google Smart Tap settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-ST-settings.htm)
