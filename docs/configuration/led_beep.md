# LED and Beep Configuration

The VTAP100 offers visual (LED) and audio (beep) feedback for various events.

## LED Settings

### LEDMode

LED operating mode.

```ini
LEDMode=0    ; LEDs off
LEDMode=1    ; LEDs on
LEDMode=2    ; Status indicator
LEDMode=3    ; Custom sequences
```

| Value | Mode | Description |
|-------|------|-------------|
| 0 | OFF | LEDs disabled |
| 1 | ON | LEDs enabled |
| 2 | STATUS | Status indicator |
| 3 | CUSTOM | Custom sequences |

### LEDSelect

Select LED type/position.

```ini
LEDSelect=0    ; External RGB LED (common cathode)
LEDSelect=1    ; On-board LED (compact case)
LEDSelect=2    ; On-board LED (square case)
LEDSelect=3    ; Serial LEDs
```

| Value | Type |
|-------|------|
| 0 | External RGB LED |
| 1 | On-board (Compact) |
| 2 | On-board (Square) |
| 3 | Serial LEDs |

### LEDDefaultRGB

Default color for LEDs (6 hex characters).

```ini
LEDDefaultRGB=FFFFFF    ; White
LEDDefaultRGB=00FF00    ; Green
LEDDefaultRGB=FF0000    ; Red
```

### LED Sequences

LED sequences can be defined for pass read, tag read, error, and start events.

**Format:** `RRGGBB,on_ms[,off_ms[,repeats]]`

| Parameter | Range | Description |
|-----------|-------|-------------|
| RRGGBB | Hex | Color (6 characters) |
| on_ms | 0-65535 | On time in ms |
| off_ms | 0-65535 | Off time in ms. May be omitted |
| repeats | 1-255 | Repetitions. May be omitted |

Trailing parameters may be left out for a single flash of the given duration.
The manufacturer's own example uses the short form:

```ini
TagLED=00FF00,500
```

A short form is written back as a short form; the tool does not expand it.

```ini
; Green blink on pass read (2x, 100ms on/off)
PassLED=00FF00,100,100,2

; Blue LED on tag read
TagLED=0000FF,100,100,1

; Red blink on error (3x fast)
PassErrorLED=FF0000,50,50,3

; Yellow LED on start
StartLED=FFFF00,500,0,1
```

## Beep/Buzzer Settings

Beep sequences can be defined for pass read, tag read, error, and start events.

**Format:** `on_ms[,off_ms[,repeats[,frequency]]]`

| Parameter | Range | Description |
|-----------|-------|-------------|
| on_ms | 0-65535 | On time in ms |
| off_ms | 0-65535 | Off time in ms. May be omitted |
| repeats | 1-255 | Repetitions. May be omitted |
| frequency | 100-20000 | Frequency in Hz. May be omitted (reader default 3136) |

The manufacturer documents omitting "the interval between beeps and number of
repeats, for a single beep of the specified duration":

```ini
TagBeep=100
```

A short form is written back as a short form.

```ini
; 2 beeps on pass read
PassBeep=100,100,2

; Short beep on tag read
TagBeep=50,50,1

; 3 beeps on error (lower tone)
PassErrorBeep=200,100,3,2000

; Long beep on start
StartBeep=500,0,1
```

## Python API

### LED Configuration

```python
from vtap100.models.feedback import (
    FeedbackConfig,
    LEDConfig,
    LEDMode,
    LEDSelect,
    LEDSequence,
)

# LED basic settings
led = LEDConfig(
    mode=LEDMode.CUSTOM,
    select=LEDSelect.ONBOARD_COMPACT,
    default_rgb="FFFFFF",
)

print(led.to_config_lines())
# ['LEDMode=3', 'LEDSelect=1', 'LEDDefaultRGB=FFFFFF']
```

### LED Sequences

```python
from vtap100.models.feedback import LEDConfig, LEDSequence

led = LEDConfig(
    pass_led=LEDSequence(color="00FF00", on_ms=100, off_ms=100, repeats=2),
    tag_led=LEDSequence(color="0000FF"),
    pass_error_led=LEDSequence(color="FF0000", on_ms=50, off_ms=50, repeats=3),
)

print(led.to_config_lines())
# ['PassLED=00FF00,100,100,2', 'TagLED=0000FF,100,100,1',
#  'PassErrorLED=FF0000,50,50,3']
```

### Beep Configuration

```python
from vtap100.models.feedback import BeepConfig, BeepSequence

beep = BeepConfig(
    pass_beep=BeepSequence(on_ms=100, off_ms=100, repeats=2),
    tag_beep=BeepSequence(on_ms=50, off_ms=50, repeats=1),
    pass_error_beep=BeepSequence(on_ms=200, off_ms=100, repeats=3, frequency=2000),
)

print(beep.to_config_lines())
# ['PassBeep=100,100,2', 'TagBeep=50,50,1', 'PassErrorBeep=200,100,3,2000']
```

### Combined Configuration

```python
from vtap100.models.feedback import (
    FeedbackConfig,
    LEDConfig,
    LEDMode,
    LEDSequence,
    BeepConfig,
    BeepSequence,
)

feedback = FeedbackConfig(
    led=LEDConfig(
        mode=LEDMode.CUSTOM,
        pass_led=LEDSequence(color="00FF00", repeats=2),
    ),
    beep=BeepConfig(
        pass_beep=BeepSequence(repeats=2),
    ),
)

print(feedback.to_config_lines())
# ['LEDMode=3', 'PassLED=00FF00,100,100,2', 'PassBeep=100,100,2']
```

### Combined with VTAPConfig

```python
from vtap100.models.config import VTAPConfig
from vtap100.models.feedback import (
    FeedbackConfig,
    LEDConfig,
    LEDMode,
    LEDSequence,
    BeepConfig,
    BeepSequence,
)
from vtap100.models.vas import AppleVASConfig
from vtap100.generator import ConfigGenerator

# Complete configuration
feedback = FeedbackConfig(
    led=LEDConfig(
        mode=LEDMode.CUSTOM,
        pass_led=LEDSequence(color="00FF00", repeats=2),
        pass_error_led=LEDSequence(color="FF0000", repeats=3),
    ),
    beep=BeepConfig(
        pass_beep=BeepSequence(repeats=2),
        pass_error_beep=BeepSequence(on_ms=200, repeats=3),
    ),
)

vas = AppleVASConfig(merchant_id="pass.com.example.mypass", key_slot=1)

config = VTAPConfig(
    vas_configs=[vas],
    feedback=feedback,
)

generator = ConfigGenerator(config)
print(generator.generate())
```

## Complete Example

```ini
!VTAPconfig
; Apple VAS Configuration
VAS1MerchantID=pass.com.example.mypass
VAS1KeySlot=1

; LED/Beep Settings
LEDMode=3
LEDSelect=1
PassLED=00FF00,100,100,2
PassErrorLED=FF0000,50,50,3
PassBeep=100,100,2
PassErrorBeep=200,100,3,2000
```

## Tips

- **LEDMode=3** is required for custom LED sequences
- Beep frequency is optional, default is 3136 Hz
- Short times (50-100ms) for quick feedback
- Longer times (200-500ms) for more noticeable signals

## See Also

- [config.txt Format](overview.md)
- [Apple VAS](apple_vas.md)
- [Google Smart Tap](google_smarttap.md)
