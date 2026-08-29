# Troubleshooting

## Reader Issues

### Reader not recognized

**Symptom:** VTAP100 drive not visible after connecting USB.

**Solutions:**
- Try a different USB port (prefer direct connection, avoid hubs)
- Check USB cable (some cables are charge-only)
- Wait 10 seconds after connecting
- On Linux: check `dmesg` for mount errors
- On macOS: check System Information → USB
- On Windows: check Device Manager

### Config not applied after reboot

**Symptom:** Changes in config.txt don't take effect.

**Solutions:**
1. Properly eject the drive before unplugging
2. Verify file is named exactly `config.txt` (case-sensitive on some systems)
3. Check file starts with `!VTAPconfig` header
4. Validate with: `vtap100 validate /path/to/config.txt`
5. Remove any BOM (byte order mark) from file

## Configuration Errors

### "merchant_id must start with 'pass.'"

Apple VAS merchant IDs must begin with `pass.` prefix.

**Fix:** Use format like `pass.com.company.passname`

### "App ID must be 6 hex characters"

DESFire App IDs must be exactly 6 hexadecimal characters.

**Fix:** Use format like `112233` or `AABBCC`

### "Key slot must be 0-6" / "Key slot must be 1-9"

- Apple VAS / Google Smart Tap: slots 1-6
- DESFire / Tag Read: slots 1-9

### Invalid config.txt syntax

**Common causes:**
- Missing `!VTAPconfig` header
- Spaces around `=` sign (use `Name=Value`, not `Name = Value`)
- Invalid characters in values
- Wrong line endings (use LF, not CRLF)

## Settings Disappear After Saving

If a setting vanishes from your `config.txt` after loading and saving it, that
is a defect — report it with the file. As of the round-trip work, all known real
configurations survive a cycle unchanged, including the manufacturer's own
published sample.

### Known limitations

Two documented syntaxes are not yet supported. A configuration using them loads,
but the affected line is dropped on save:

- **Sequence references** (firmware v5+): `TagBeep=100:tagbeep@beeps.ini` and
  `LEDDefaultRGB=FFFFFF:seq.comet@leds.ini`, which point at entries in
  `leds.ini` or `beeps.ini`.
- **Bluetooth, OSDP and MIFARE Classic settings** are not modelled at all.

## Key File Issues

### Pass not reading / Authentication failed

**Check:**
1. Private key file exists (`private1.pem` to `private6.pem`)
2. Key slot in config matches file number
3. Key format is correct (ECDSA P-256 for Apple/Google)
4. Key matches the one registered in Apple/Google dashboard

### Key file not found

Place key files in the VTAP100 root directory:
```
/media/user/VTAP100/
├── config.txt
├── private1.pem
├── private2.pem
└── ...
```

## Pass Reading Issues

### Apple VAS pass not detected

- Verify Pass Type ID matches exactly (case-sensitive)
- Check iPhone NFC is enabled
- Hold phone close to reader for 2-3 seconds
- Ensure pass is in Apple Wallet (not just downloaded)

### Google Smart Tap pass not detected

- **ST1 configuration does not work** - use ST2 and higher (ST2CollectorID, ST2KeySlot, etc.)
- Verify Collector ID is correct (numeric)
- Key version must match Google dashboard
- Android: only one Collector ID active at a time
- Check Google Pay app has the pass

### NFC tag not reading

- Verify correct NFCType is enabled (2, 4, or 5)
- Check tag is compatible with selected mode
- For block reading: verify key slot and key type
- Some tags require specific authentication

## Keyboard Output Issues

### No keyboard output

1. Check `KBLogMode=1` is set
2. Verify `KBEnable=1` (default)
3. Check `KBSource` includes your data type (A, G, 2, 4, etc.)
4. Test with a text editor open and focused

### Wrong characters output

- Check `KBDelayMS` - increase if characters are skipped
- Verify keyboard layout matches reader configuration
- Check `KBPostfix` / `KBPrefix` values

## LED/Beep Issues

### LEDs not working

1. Check `LEDMode` is not 0 (off)
2. Verify `LEDSelect` matches your hardware (0-3)
3. For custom sequences: check color format is 6 hex chars

### No beep sound

- Some VTAP100 models don't have a buzzer
- Check beep sequence format: `on_ms,off_ms,repeats`
- Verify frequency is in valid range (100-20000 Hz)

## Getting Help

- Validate config: `vtap100 validate config.txt`
- Show docs: `vtap100 docs`
- Official support: vtap-support@dotorigin.com
- [VTAP Help Center](https://help.vtapnfc.com/)
