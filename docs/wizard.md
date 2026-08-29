# Wizard Guide

The interactive wizard guides you through VTAP100 configuration step by step.

## Start

```bash
vtap100 wizard
```

Press `Enter` for defaults, `Ctrl+C` to cancel.

## Steps

### 1. Apple VAS

- Configure Apple VAS? (y/n)
- Pass Type ID (e.g., `pass.com.example.myapp`)
- Key slot (1-6)

### 2. Google Smart Tap

- Configure Google Smart Tap? (y/n)
- Collector ID
- Key slot (1-6)
- Key version

### 3. NFC Tags

- Configure NFC Tags? (y/n)
- Type 2 mode (0=off, U=UID, N=NDEF, B=block)
- Type 4 mode (0=off, U=UID, N=NDEF, B=block, D=DESFire)
- Type 5 mode (0=off, U=UID, N=NDEF, B=block)

### 4. DESFire

- Configure DESFire? (y/n)
- App ID (6 hex chars)
- File ID (0-255)
- Key slot (1-9)
- Crypto mode (0=none, 1=3DES, 3=AES)

### 5. Keyboard Emulation

- Configure keyboard? (y/n)
- Enable keyboard output (y/n)
- Data source (e.g., A=Apple, G=Google, AG=both)

### 6. LED/Beep Feedback

- Configure LED/Beep? (y/n)
- LED mode (0=off, 1=on, 2=status, 3=custom)
- Pass LED color (hex, e.g., 00FF00)
- Beep settings

### 7. Output

- Output file path (default: config.txt)
- Preview and confirm

## Tips

- Skip sections by answering "n" to configure questions
- The wizard validates input in real-time
- Generated config is displayed before saving
- For advanced options, use the TUI editor: `vtap100 editor`
