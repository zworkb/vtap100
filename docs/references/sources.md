# VTAP100 Reference Sources

This page contains all sources and additional links for VTAP100 documentation.

## Official Documentation

### PDFs for Download
- [VTAP Configuration Guide (PDF)](https://www.vtapnfc.com/downloads/VTAP_Configuration_Guide.pdf) - Main configuration documentation
- [VTAP Commands Reference Guide (PDF)](https://www.vtapnfc.com/downloads/VTAP_Commands_Reference_Guide.pdf) - Complete parameter reference
- [VTAP Documentation Portal](https://www.vtapnfc.com/documentation/) - Overview page of all documents

## VTAP Help Center

Online documentation with detailed parameter descriptions:

### Configuration Parameters
- [Apple VAS Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-VAS_settings.htm) - Apple Value Added Services
- [Google Smart Tap Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-ST-settings.htm) - Google Wallet Smart Tap
- [Keyboard Emulation Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-KB-settings.htm) - Keyboard emulation
- [NFC Card/Tag Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Card-Tag-settings.htm) - NFC tag types
- [MIFARE Classic Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-MIFARE-settings.htm) - MIFARE Classic cards
- [DESFire Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-DESFire-settings.htm) - MIFARE DESFire
- [Access Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-Access-settings.htm) - Apple Access (ECP2): AccessTCI, AccessAuthRequired, ECP2Mode
- [Control the LEDs or buzzer](https://help.vtapnfc.com/en/Content/VTAP-Configuration-Guide/Control-the-LEDs-or-buzzer.htm) - Beep sequences and their short forms
- [LED Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-LED-settings.htm) - LED control
- [Bluetooth Settings](https://help.vtapnfc.com/en/Content/VTAP-Commands/Config-txt-BT-settings.htm) - Bluetooth BLE

### Configuration Files
- [Default config.txt](https://help.vtapnfc.com/en/Content/VTAP-Configuration-Guide/VTAPConfig-txt.htm) - Default configuration
- [Downloadable sample config.txt](https://www.vtapnfc.com/downloads/config.txt) - The manufacturer's published example, kept verbatim as `tests/fixtures/valid_configs/vendor_sample.txt`
- [Default leds.ini](https://help.vtapnfc.com/en/Content/VTAP-Configuration-Guide/LEDS-ini.htm) - LED sequences
- [Dynamic Configuration Commands](https://help.vtapnfc.com/en/Content/VTAP-Commands/Dynamic-config-commands.htm) - Dynamic commands
- [Control LED and Buzzer Feedback](https://help.vtapnfc.com/en/Content/VTAP-Configuration-Guide/Control-the-LEDs-or-buzzer.htm) - LED/Buzzer control

## Third-Party Tutorials

### PassNinja
- [How to configure a Dot Origin VTAP100 NFC reader](https://www.passninja.com/tutorials/hardware/how-to-configure-a-dot-origin-vtap100-nfc-reader) - Comprehensive tutorial

### Passmeister
- [Apple Wallet NFC Setup (EN)](https://www.passmeister.com/en/b/nfc_setup_dot_origin_vtap100_apple_wallet) - Apple VAS setup
- [Apple Wallet NFC Setup (DE)](https://www.passmeister.com/de/b/nfc_setup_dot_origin_vtap100_apple_wallet) - German version
- [Google Wallet NFC Setup (EN)](https://www.passmeister.com/en/b/nfc_setup_dot_origin_vtap100_google_wallet) - Google Smart Tap setup
- [Google Wallet NFC Setup (DE)](https://www.passmeister.com/de/b/nfc_setup_dot_origin_vtap100_google_wallet) - German version

### AccessGrid
- [Configuring a VTAP reader](https://www.accessgrid.com/guides/nfc-readers/configuring-a-vtap-reader) - AccessGrid integration

## Manuals (ManualsLib)

PDF manuals for online reading or download:

- [VTAP100 Installation Manual](https://www.manualslib.com/manual/2914074/Dot-Origin-Vtap100.html) - Desktop USB reader
- [VTAP100 Basic Configuration Manual](https://www.manualslib.com/manual/2904969/Dot-Origin-Vtap-100.html) - Basic configuration
- [VTAP100-PAC-W Installation Manual](https://www.manualslib.com/manual/3279356/Dot-Origin-Vtap100-Pac-W.html) - Wiegand reader
- [VTAP100 User Manual (PoE)](https://www.manualslib.com/manual/3562854/Dot-Origin-Vtap100.html) - Cloud-enabled reader
- [VTAP Series Integration Manual](https://www.manualslib.com/manual/3364754/Dot-Origin-Vtap-Series.html) - Integration guide
- [Dot Origin Brand Manuals](https://www.manualslib.com/brand/dot-origin/) - All Dot Origin manuals

## Manufacturer Websites

- [Dot Origin Website](https://www.dotorigin.com/) - Manufacturer homepage
- [Dot Origin Products](https://www.dotorigin.com/products/vtap-mobile-nfc-pass-readers/) - VTAP product overview
- [VTAP NFC Website](https://www.vtapnfc.com/) - Product website
- [VTAP Shop](https://shop.vtapnfc.com/) - Online shop
- [VTAP100 USB Product Page](https://shop.vtapnfc.com/product/vtap100-mobile-wallet-nfc-reader-usb/) - USB variant
- [VTAP100 OEM Board](https://shop.vtapnfc.com/product/vtap100-embedded-nfc-reader-board/) - Embedded board

## Support

- **Email:** vtap-support@dotorigin.com
- **Knowledge Base:** [help.vtapnfc.com](https://help.vtapnfc.com/)

## Technical Standards

### Apple
- [Apple Wallet Developer Documentation](https://developer.apple.com/documentation/walletpasses) - Apple Pass development
- [Apple VAS Developer Forums](https://developer.apple.com/forums/thread/47872) - VAS discussions

### Google
- [Google Wallet API](https://developers.google.com/wallet) - Google Wallet development
- [Smart Tap Protocol (GitHub)](https://github.com/kormax/google-smart-tap) - Smart Tap protocol analysis

### NFC/MIFARE
- [NXP MIFARE DESFire](https://www.nxp.com/products/rfid-nfc/mifare-hf/mifare-desfire:MC_53450) - DESFire product page
- [NXP AN10922](https://www.nxp.com/docs/en/application-note/AN10922.pdf) - Key diversification

---

These pages are the authority for every documented value range in this project.
Where the repository's own documentation disagreed with them, the manufacturer
won — see `docs/superpowers/specs/2026-08-28-config-roundtrip-design.md` section 9
for the quoted ranges.

*Last updated: 2026-08-29*
