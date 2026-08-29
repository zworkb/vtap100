# Python API

Use vtap100 as a library to create, parse, modify, and generate configurations.

## Installation

```bash
pip install vtap100
```

## Quick Start

```python
from vtap100.models.config import VTAPConfig
from vtap100.models.vas import AppleVASConfig
from vtap100.generator import ConfigGenerator
from vtap100.parser import parse

# Create config
vas = AppleVASConfig(merchant_id="pass.com.example.myapp", key_slot=1)
config = VTAPConfig(vas_configs=[vas])

# Generate config.txt
generator = ConfigGenerator(config)
print(generator.generate())
```

## Creating Configurations

### Apple VAS

```python
from vtap100.models.vas import AppleVASConfig

vas = AppleVASConfig(
    merchant_id="pass.com.example.myapp",  # required, must start with "pass."
    key_slot=1,                             # optional, 0-6 (0 or omitted = automatic)
    merchant_url="https://example.com",     # optional
)
```

### Google Smart Tap

```python
from vtap100.models.smarttap import GoogleSmartTapConfig

st = GoogleSmartTapConfig(
    collector_id="96972794",  # required
    key_slot=2,               # optional, 0-6 (0 or omitted = default)
    key_version=1,            # must match Google dashboard
)
```

### Keyboard Emulation

```python
from vtap100.models.keyboard import KeyboardConfig, KBSourceBuilder

kb = KeyboardConfig(
    log_mode=True,       # enable keyboard output
    source="81",         # hex bitmask (0x80=mobile pass, 0x01=UID)
    prefix="$t",         # optional prefix ($t=timestamp)
    postfix="%0A",       # suffix (default=newline)
    delay_ms=5,          # keystroke delay 5-255ms
)

# Or use the builder for source:
source = KBSourceBuilder().mobile_pass().card_tag_uid().build()  # "81"
```

### NFC Tags

```python
from vtap100.models.nfc import NFCTagConfig, NFCTagMode, TagReadConfig

nfc = NFCTagConfig(
    type2=NFCTagMode.UID,   # 0=off, U=UID, N=NDEF, B=block
    type4=NFCTagMode.NDEF,
    type5=NFCTagMode.DISABLED,
)

# With block reading:
nfc = NFCTagConfig(
    type2=NFCTagMode.BLOCK,
    tag_read=TagReadConfig(block_num=4, key_slot=1, length=16),
)
```

### DESFire

```python
from vtap100.models.desfire import DESFireConfig, DESFireAppConfig, DESFireCryptoMode

desfire = DESFireConfig(
    apps=[
        DESFireAppConfig(
            app_id="112233",              # 6 hex chars
            file_id=1,
            key_slot=1,
            crypto=DESFireCryptoMode.AES, # 0=none, 1=3DES, 3=AES
        )
    ]
)
```

### LED/Beep Feedback

```python
from vtap100.models.feedback import (
    FeedbackConfig, LEDConfig, BeepConfig,
    LEDSequence, BeepSequence, LEDMode
)

feedback = FeedbackConfig(
    led=LEDConfig(
        mode=LEDMode.CUSTOM,
        pass_led=LEDSequence(color="00FF00", on_ms=100, off_ms=100, repeats=2),
    ),
    beep=BeepConfig(
        pass_beep=BeepSequence(on_ms=100, off_ms=50, repeats=1),
    ),
)
```

### Combined Configuration

```python
from vtap100.models.config import VTAPConfig

config = VTAPConfig(
    vas_configs=[vas],
    smarttap_configs=[st],
    keyboard=kb,
    nfc=nfc,
    desfire=desfire,
    feedback=feedback,
)
```

## Generating config.txt

```python
from vtap100.generator import ConfigGenerator
from pathlib import Path

generator = ConfigGenerator(config)

# As string
content = generator.generate(comment="My config")
print(content)

# To file
generator.write_to_file(Path("config.txt"))

# Jinja2 template (for dynamic pass lists)
template = generator.generate_template()
```

## Parsing Existing Configs

```python
from vtap100.parser import parse
from pathlib import Path

# From string
content = Path("config.txt").read_text()
config = parse(content)

# Access parsed data
for vas in config.vas_configs:
    print(f"Apple VAS: {vas.merchant_id}, slot {vas.key_slot}")

for st in config.smarttap_configs:
    print(f"Google ST: {st.collector_id}")

if config.keyboard:
    print(f"Keyboard: source={config.keyboard.source}")
```

## Modifying Configurations

Pydantic models are immutable by default. Use `model_copy()`:

```python
# Modify a VAS config
new_vas = vas.model_copy(update={"key_slot": 2})

# Modify the main config
new_config = config.model_copy(update={
    "vas_configs": [new_vas],
    "keyboard": KeyboardConfig(log_mode=True, source="81"),
})

# Add to lists
updated_vas_list = config.vas_configs + [new_vas]
new_config = config.model_copy(update={"vas_configs": updated_vas_list})
```

## Round-Trip Example

```python
from vtap100.parser import parse
from vtap100.generator import ConfigGenerator
from pathlib import Path

# Load existing config
content = Path("/media/user/VTAP100/config.txt").read_text()
config = parse(content)

# Modify
new_kb = KeyboardConfig(log_mode=True, source="A5")
config = config.model_copy(update={"keyboard": new_kb})

# Save back
generator = ConfigGenerator(config)
generator.write_to_file(Path("/media/user/VTAP100/config.txt"))
```

## Model Reference

| Import | Class |
|--------|-------|
| `vtap100.models.config` | `VTAPConfig` |
| `vtap100.models.vas` | `AppleVASConfig` |
| `vtap100.models.smarttap` | `GoogleSmartTapConfig` |
| `vtap100.models.keyboard` | `KeyboardConfig`, `KBSourceBuilder` |
| `vtap100.models.nfc` | `NFCTagConfig`, `NFCTagMode`, `TagReadConfig` |
| `vtap100.models.desfire` | `DESFireConfig`, `DESFireAppConfig` |
| `vtap100.models.feedback` | `FeedbackConfig`, `LEDConfig`, `BeepConfig` |
| `vtap100.generator` | `ConfigGenerator` |
| `vtap100.parser` | `parse()` |
