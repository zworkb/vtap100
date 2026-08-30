# Apple VAS Configuration

Apple VAS (Value Added Services) enables reading Apple Wallet passes via NFC. The VTAP100 is Apple certified for VAS transactions.

## Prerequisites

1. Apple Developer Account
2. Apple Wallet NFC certificate (Pass Type ID)
3. Private key in PEM format

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| VAS#MerchantID | String | - | **Required.** Apple Pass Type ID (e.g., `pass.com.company.passname`) |
| VAS#KeySlot | 0-6 | omitted | Slot of the private#.pem file. Optional: 0 or omitted makes the reader compare all available keys against the hash of the public key |
| VAS#MerchantURL | URL | - | Optional: URL for pass presentation |
| VASDefaultPassesEnabled | List | 1,2,3,4,5,6 | Active VAS configurations |

*`#` = Slot number 1-6 for up to 6 different pass types*

## CLI Examples

### Simple Configuration

```bash
vtap100 generate --apple-vas pass.com.example.myapp --key-slot 1
```

### With Output File

```bash
vtap100 generate \
  --apple-vas pass.com.example.myapp \
  --key-slot 1 \
  --output /media/VTAP100/config.txt
```

## Python API

```python
from vtap100.models.vas import AppleVASConfig
from vtap100.models.config import VTAPConfig
from vtap100.generator import ConfigGenerator

# Single VAS configuration
vas = AppleVASConfig(
    merchant_id="pass.com.example.myapp",
    key_slot=1,
)

# Multiple VAS configurations
vas1 = AppleVASConfig(merchant_id="pass.com.example.loyalty", key_slot=1)
vas2 = AppleVASConfig(merchant_id="pass.com.example.membership", key_slot=2)

config = VTAPConfig(vas_configs=[vas1, vas2])
generator = ConfigGenerator(config)
print(generator.generate())
```

## Generated config.txt

```ini
!VTAPconfig
; Apple VAS Configuration
VAS1MerchantID=pass.com.example.myapp
VAS1KeySlot=1
```

## Key File Setup

1. Export your private Apple VAS key as a PEM file
2. Name the file `private1.pem` (for KeySlot=1)
3. Copy the file to the VTAP100
4. After reboot, the key is stored in hardware

**Important:** The key disappears from the filesystem after reboot but is securely stored in the reader.

## Validation

The generator automatically validates:
- Merchant ID must start with `pass.`
- Key slot must be between 0 and 6
- Merchant ID cannot be empty

```python
from vtap100.models.vas import AppleVASConfig
from pydantic import ValidationError

try:
    # This will throw an error
    vas = AppleVASConfig(merchant_id="invalid.id")
except ValidationError as e:
    print(e)  # "merchant_id must start with 'pass.' prefix"
```

## References

- [VTAP Help - Apple VAS Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-VAS_settings.htm)
- [Passmeister - Apple Wallet Setup](https://www.passmeister.com/en/b/nfc_setup_dot_origin_vtap100_apple_wallet)

## Manufacturer Documentation

The authority for every value range on this page. Where this project's
documentation disagreed with these, the manufacturer won.

- [Apple VAS settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-VAS_settings.htm)
