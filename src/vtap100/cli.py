"""Command-line interface for VTAP100 Configuration Generator.

This module provides a Rich CLI for generating VTAP100 configuration files.
Supports both command-line arguments and an interactive wizard mode.

Example:
    $ vtap100 generate --apple-vas pass.com.example.test --key-slot 1
    $ vtap100 wizard
    $ vtap100 validate config.txt
"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from vtap100 import __version__
from vtap100.generator import ConfigGenerator
from vtap100.models.config import VTAPConfig
from vtap100.models.desfire import DESFireAppConfig
from vtap100.models.desfire import DESFireConfig
from vtap100.models.desfire import DESFireCryptoMode
from vtap100.models.feedback import BeepConfig
from vtap100.models.feedback import BeepSequence
from vtap100.models.feedback import FeedbackConfig
from vtap100.models.feedback import LEDConfig
from vtap100.models.feedback import LEDMode
from vtap100.models.feedback import LEDSequence
from vtap100.models.keyboard import KeyboardConfig
from vtap100.models.nfc import NFCTagConfig
from vtap100.models.nfc import NFCTagMode
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.models.vas import AppleVASConfig


console = Console()


def print_header() -> None:
    """Print the CLI header with version info."""
    console.print(
        Panel.fit(
            f"[bold blue]VTAP100 Editor[/bold blue] [dim]{__version__}[/dim]",
            border_style="blue",
        )
    )


def print_config_preview(config_text: str) -> None:
    """Print a syntax-highlighted preview of the config.

    Args:
        config_text: The config.txt content to display.
    """
    syntax = Syntax(config_text, "ini", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Generated config.txt", border_style="green"))


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: The success message to display.
    """
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: The error message to display.
    """
    console.print(f"[bold red]✗[/bold red] {message}")


def print_section(title: str) -> None:
    """Print a section header.

    Args:
        title: The section title.
    """
    console.print(f"\n[bold cyan]━━━ {title} ━━━[/bold cyan]\n")


@click.group()
@click.version_option(version=__version__, prog_name="vtap100")
def main() -> None:
    """VTAP100 Configuration Generator - Create config files for Dot Origin VTAP100 NFC readers."""
    pass


@main.command()
@click.option(
    "--apple-vas",
    "-a",
    help="Apple VAS Merchant ID (e.g., pass.com.example.myapp)",
)
@click.option(
    "--google-st",
    "-g",
    help="Google Smart Tap Collector ID",
)
@click.option(
    "--key-slot",
    "-k",
    type=click.IntRange(0, 6),
    default=1,
    help="Key slot for the pass (0-6; 0 lets the reader select automatically)",
)
@click.option(
    "--key-version",
    type=int,
    default=1,
    help="Key version for Google Smart Tap",
)
@click.option(
    "--keyboard/--no-keyboard",
    default=True,
    help="Enable keyboard emulation",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True),
    default="config.txt",
    help="Output file path",
)
@click.option(
    "--comment",
    "-c",
    help="Comment to add to the config file",
)
def generate(
    apple_vas: str | None,
    google_st: str | None,
    key_slot: int,
    key_version: int,
    keyboard: bool,
    output: str,
    comment: str | None,
) -> None:
    """Generate a VTAP100 config.txt file.

    Examples:
        vtap100 generate --apple-vas pass.com.example.myapp --key-slot 1
        vtap100 generate --google-st 96972794 --key-slot 2 --key-version 1
        vtap100 generate -a pass.com.example.myapp -g 96972794 -k 1
    """
    print_header()

    if not apple_vas and not google_st:
        print_error("Please provide at least --apple-vas or --google-st")
        raise click.Abort()

    # Build configuration
    vas_configs: list[AppleVASConfig] = []
    st_configs: list[GoogleSmartTapConfig] = []

    if apple_vas:
        try:
            vas = AppleVASConfig(slot=1, merchant_id=apple_vas, key_slot=key_slot)
            vas_configs.append(vas)
            console.print("\n[bold]Apple VAS Configuration[/bold]")
            console.print(f"  Merchant ID: [cyan]{apple_vas}[/cyan]")
            console.print(f"  Key Slot:    [cyan]{key_slot}[/cyan]")
        except ValueError as e:
            print_error(f"Invalid Apple VAS configuration: {e}")
            raise click.Abort() from None

    if google_st:
        try:
            st = GoogleSmartTapConfig(
                slot=2,
                collector_id=google_st,
                key_slot=key_slot,
                key_version=key_version,
            )
            st_configs.append(st)
            console.print("\n[bold]Google Smart Tap Configuration[/bold]")
            console.print(f"  Collector ID: [cyan]{google_st}[/cyan]")
            console.print(f"  Key Slot:     [cyan]{key_slot}[/cyan]")
            console.print(f"  Key Version:  [cyan]{key_version}[/cyan]")
        except ValueError as e:
            print_error(f"Invalid Google Smart Tap configuration: {e}")
            raise click.Abort() from None

    # Keyboard emulation
    kb_config = None
    if keyboard:
        # Determine source based on configured passes
        sources = []
        if vas_configs:
            sources.append("A")
        if st_configs:
            sources.append("G")
        source = "".join(sources) + "1" if sources else "A1"

        kb_config = KeyboardConfig(log_mode=True, source=source)
        console.print("\n[bold]Keyboard Emulation[/bold]")
        console.print("  Mode:   [green]Enabled[/green]")
        console.print(f"  Source: [cyan]{source}[/cyan]")

    # Create config
    config = VTAPConfig(
        vas_configs=vas_configs,
        smarttap_configs=st_configs,
        keyboard=kb_config,
    )

    # Generate
    generator = ConfigGenerator(config)
    config_text = generator.generate(comment=comment or "Generated by VTAP100 CLI")

    console.print()
    print_config_preview(config_text)

    # Write file
    output_path = Path(output)
    generator.write_to_file(output_path, comment=comment or "Generated by VTAP100 CLI")
    console.print()
    print_success(f"Configuration saved to: {output_path}")


@main.command()
def wizard() -> None:
    """Interactive wizard for creating a VTAP100 configuration.

    Guides you step-by-step through creating a configuration file.
    Supports all features: Apple VAS, Google Smart Tap, NFC Tags,
    DESFire, Keyboard Emulation, and LED/Beep feedback.
    """
    print_header()
    console.print("\n[bold]Interactive Configuration Wizard[/bold]")
    console.print("[dim]Drücke Enter für Standardwerte, Ctrl+C zum Abbrechen[/dim]\n")

    vas_configs: list[AppleVASConfig] = []
    st_configs: list[GoogleSmartTapConfig] = []
    nfc_config: NFCTagConfig | None = None
    desfire_config: DESFireConfig | None = None
    kb_config: KeyboardConfig | None = None
    feedback_config: FeedbackConfig | None = None

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 1: Apple VAS
    # ═══════════════════════════════════════════════════════════════════
    print_section("Apple VAS")
    if click.confirm("Apple VAS konfigurieren?", default=False):
        merchant_id = click.prompt(
            "Apple Pass Type ID (z.B. pass.com.example.myapp)",
            type=str,
        )
        key_slot = click.prompt("Key slot (0-6, 0=automatic)", type=int, default=0)

        try:
            vas = AppleVASConfig(slot=1, merchant_id=merchant_id, key_slot=key_slot)
            vas_configs.append(vas)
            print_success("Apple VAS konfiguriert")
        except ValueError as e:
            print_error(f"Ungültige Konfiguration: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 1: Google Smart Tap
    # ═══════════════════════════════════════════════════════════════════
    print_section("Google Smart Tap")
    if click.confirm("Google Smart Tap konfigurieren?", default=False):
        collector_id = click.prompt("Google Collector ID", type=str)
        key_slot = click.prompt("Key slot (0-6, 0=automatic)", type=int, default=0)
        key_version = click.prompt("Key-Version", type=int, default=1)

        try:
            st = GoogleSmartTapConfig(
                slot=2,
                collector_id=collector_id,
                key_slot=key_slot,
                key_version=key_version,
            )
            st_configs.append(st)
            print_success("Google Smart Tap konfiguriert")
        except ValueError as e:
            print_error(f"Ungültige Konfiguration: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 3: NFC Tags
    # ═══════════════════════════════════════════════════════════════════
    print_section("NFC Tags")
    if click.confirm("NFC Tags konfigurieren?", default=False):
        console.print("[dim]Modi: 0=Aus, U=UID, N=NDEF, B=Block, D=DESFire (nur Type4)[/dim]")

        type2_mode = click.prompt(
            "NFC Type 2 Modus (NTAG, Ultralight)",
            type=click.Choice(["0", "U", "N", "B"]),
            default="0",
        )
        type4_mode = click.prompt(
            "NFC Type 4 Modus (DESFire, ISO14443-4)",
            type=click.Choice(["0", "U", "N", "B", "D"]),
            default="0",
        )
        type5_mode = click.prompt(
            "NFC Type 5 Modus (ICODE, ISO15693)",
            type=click.Choice(["0", "U", "N", "B"]),
            default="0",
        )

        mode_map = {
            "0": NFCTagMode.DISABLED,
            "U": NFCTagMode.UID,
            "N": NFCTagMode.NDEF,
            "B": NFCTagMode.BLOCK,
            "D": NFCTagMode.DESFIRE,
        }

        nfc_config = NFCTagConfig(
            type2=mode_map[type2_mode] if type2_mode != "0" else None,
            type4=mode_map[type4_mode] if type4_mode != "0" else None,
            type5=mode_map[type5_mode] if type5_mode != "0" else None,
        )

        if click.confirm("Zufällige UIDs ignorieren?", default=False):
            nfc_config.ignore_random_uid = True

        print_success("NFC Tags konfiguriert")

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 4: MIFARE DESFire
    # ═══════════════════════════════════════════════════════════════════
    print_section("MIFARE DESFire")
    if click.confirm("MIFARE DESFire konfigurieren?", default=False):
        desfire_apps: list[DESFireAppConfig] = []

        while len(desfire_apps) < 9:
            app_id = click.prompt(
                f"DESFire App {len(desfire_apps) + 1} - App ID (6 Hex-Zeichen, leer=Ende)",
                default="",
            )
            if not app_id:
                break

            try:
                file_id = click.prompt("File ID (0-255, empty=skip)", type=int, default=0)
                key_slot = click.prompt("Key slot (1-9, 0=none)", type=int, default=0)

                crypto_choice = click.prompt(
                    "Crypto (0=Keine, 1=3DES, 3=AES)",
                    type=click.Choice(["0", "1", "3"]),
                    default="0",
                )
                crypto_map = {
                    "0": None,
                    "1": DESFireCryptoMode.DES3,
                    "3": DESFireCryptoMode.AES,
                }

                app = DESFireAppConfig(
                    app_id=app_id,
                    file_id=file_id if file_id > 0 else None,
                    key_slot=key_slot if key_slot > 0 else None,
                    crypto=crypto_map[crypto_choice],
                )
                desfire_apps.append(app)
                print_success(f"DESFire App {len(desfire_apps)} hinzugefügt")

            except ValueError as e:
                print_error(f"Ungültige Konfiguration: {e}")

            if not click.confirm("Weitere DESFire App hinzufügen?", default=False):
                break

        if desfire_apps:
            desfire_config = DESFireConfig(apps=desfire_apps)
            print_success(f"{len(desfire_apps)} DESFire App(s) konfiguriert")

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 1+2: Keyboard Emulation
    # ═══════════════════════════════════════════════════════════════════
    print_section("Keyboard Emulation")
    if click.confirm("Keyboard-Emulation aktivieren?", default=True):
        # Determine source based on configured passes
        sources = []
        if vas_configs:
            sources.append("A")
        if st_configs:
            sources.append("G")
        if nfc_config and (nfc_config.type2 or nfc_config.type4 or nfc_config.type5):
            # Add NFC sources based on configured types
            if nfc_config.type2:
                sources.append("2")
            if nfc_config.type4:
                sources.append("4")
            if nfc_config.type5:
                sources.append("5")
        if desfire_config and desfire_config.apps:
            sources.append("D")

        default_source = "".join(sources) + "1" if sources else "A1"
        source = click.prompt("KBSource", default=default_source)

        # Extended keyboard options (Phase 2)
        prefix = None
        postfix = "%0A"
        delay_ms = 5

        if click.confirm("Erweiterte Keyboard-Optionen?", default=False):
            prefix_input = click.prompt("Prefix (leer=keins)", default="")
            if prefix_input:
                prefix = prefix_input

            postfix = click.prompt("Postfix", default="%0A")
            delay_ms = click.prompt("Delay zwischen Tasten (ms, 5-255)", type=int, default=5)

        kb_config = KeyboardConfig(
            log_mode=True,
            source=source,
            prefix=prefix,
            postfix=postfix,
            delay_ms=delay_ms,
        )
        print_success("Keyboard-Emulation konfiguriert")

    # ═══════════════════════════════════════════════════════════════════
    # PHASE 5: LED/Beep Feedback
    # ═══════════════════════════════════════════════════════════════════
    print_section("LED/Beep Feedback")
    if click.confirm("LED/Beep Feedback konfigurieren?", default=False):
        led_config: LEDConfig | None = None
        beep_config: BeepConfig | None = None

        # LED Configuration
        if click.confirm("LED konfigurieren?", default=True):
            led_mode_choice = click.prompt(
                "LED-Modus (0=Aus, 1=An, 2=Status, 3=Custom)",
                type=click.Choice(["0", "1", "2", "3"]),
                default="3",
            )
            led_mode_map = {
                "0": LEDMode.OFF,
                "1": LEDMode.ON,
                "2": LEDMode.STATUS,
                "3": LEDMode.CUSTOM,
            }

            pass_led = None
            error_led = None

            if led_mode_choice == "3":
                # Custom LED sequences
                if click.confirm("LED für erfolgreichen Scan?", default=True):
                    color = click.prompt("Farbe (Hex, z.B. 00FF00)", default="00FF00")
                    repeats = click.prompt("Wiederholungen", type=int, default=2)
                    pass_led = LEDSequence(color=color, repeats=repeats)

                if click.confirm("LED für Fehler?", default=True):
                    color = click.prompt("Farbe (Hex, z.B. FF0000)", default="FF0000")
                    repeats = click.prompt("Wiederholungen", type=int, default=3)
                    error_led = LEDSequence(color=color, repeats=repeats)

            led_config = LEDConfig(
                mode=led_mode_map[led_mode_choice],
                pass_led=pass_led,
                pass_error_led=error_led,
            )
            print_success("LED konfiguriert")

        # Beep Configuration
        if click.confirm("Beep konfigurieren?", default=True):
            pass_beep = None
            error_beep = None

            if click.confirm("Beep für erfolgreichen Scan?", default=True):
                repeats = click.prompt("Wiederholungen", type=int, default=2)
                pass_beep = BeepSequence(repeats=repeats)

            if click.confirm("Beep für Fehler?", default=True):
                repeats = click.prompt("Wiederholungen", type=int, default=3)
                on_ms = click.prompt("An-Zeit (ms)", type=int, default=200)
                error_beep = BeepSequence(on_ms=on_ms, repeats=repeats)

            beep_config = BeepConfig(
                pass_beep=pass_beep,
                pass_error_beep=error_beep,
            )
            print_success("Beep konfiguriert")

        if led_config or beep_config:
            feedback_config = FeedbackConfig(led=led_config, beep=beep_config)

    # ═══════════════════════════════════════════════════════════════════
    # Output
    # ═══════════════════════════════════════════════════════════════════
    print_section("Ausgabe")
    output = click.prompt("Ausgabedatei", default="config.txt")

    # Create and generate
    config = VTAPConfig(
        vas_configs=vas_configs,
        smarttap_configs=st_configs,
        nfc=nfc_config,
        desfire=desfire_config,
        keyboard=kb_config,
        feedback=feedback_config,
    )

    generator = ConfigGenerator(config)
    config_text = generator.generate(comment="Generated by VTAP100 Wizard")

    console.print()
    print_config_preview(config_text)

    if click.confirm("\nKonfiguration speichern?", default=True):
        output_path = Path(output)
        generator.write_to_file(output_path, comment="Generated by VTAP100 Wizard")
        print_success(f"Konfiguration gespeichert: {output_path}")


@main.command()
@click.argument("config_file", type=click.Path(exists=True, dir_okay=False))
def validate(config_file: str) -> None:
    """Validate an existing config.txt file.

    Args:
        config_file: Path to the config.txt file to validate.
    """
    print_header()
    console.print(f"\n[bold]Validating:[/bold] {config_file}\n")

    config_path = Path(config_file)
    content = config_path.read_text()

    # Basic validation
    errors: list[str] = []
    warnings: list[str] = []

    if not content.startswith("!VTAPconfig"):
        errors.append("File must start with '!VTAPconfig'")

    lines = content.split("\n")
    for i, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith(";") or line.startswith("!"):
            continue
        if "=" not in line:
            errors.append(f"Line {i}: Invalid format (missing '='): {line}")

    # Display results
    if errors:
        console.print("[bold red]Errors found:[/bold red]")
        for error in errors:
            console.print(f"  [red]• {error}[/red]")
    else:
        print_success("No errors found")

    if warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in warnings:
            console.print(f"  [yellow]• {warning}[/yellow]")

    # Show content
    console.print()
    syntax = Syntax(content, "ini", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=config_file, border_style="blue"))


@main.command()
def docs() -> None:
    """Show documentation about VTAP100 configuration parameters."""
    print_header()

    # VAS Parameters
    console.print("\n[bold cyan]━━━ Apple VAS Parameters ━━━[/bold cyan]")
    vas_table = Table(show_header=True, header_style="bold")
    vas_table.add_column("Parameter", style="cyan")
    vas_table.add_column("Values")
    vas_table.add_column("Description")
    vas_table.add_row("VAS#MerchantID", "String", "Apple Pass Type ID (pass.com.*)")
    vas_table.add_row("VAS#KeySlot", "0-6", "Private key slot, optional (0=auto)")
    vas_table.add_row("VAS#MerchantURL", "URL", "Optional URL for pass")
    console.print(vas_table)

    # Smart Tap Parameters
    console.print("\n[bold cyan]━━━ Google Smart Tap Parameters ━━━[/bold cyan]")
    st_table = Table(show_header=True, header_style="bold")
    st_table.add_column("Parameter", style="cyan")
    st_table.add_column("Values")
    st_table.add_column("Description")
    st_table.add_row("ST#CollectorID", "String", "Google Collector ID")
    st_table.add_row("ST#KeySlot", "0-6", "Private key slot, optional (0=default)")
    st_table.add_row("ST#KeyVersion", "Integer", "Key version number")
    console.print(st_table)

    # NFC Tag Parameters
    console.print("\n[bold cyan]━━━ NFC Tag Parameters ━━━[/bold cyan]")
    nfc_table = Table(show_header=True, header_style="bold")
    nfc_table.add_column("Parameter", style="cyan")
    nfc_table.add_column("Values")
    nfc_table.add_column("Description")
    nfc_table.add_row("NFCType2", "0,U,N,B", "Type 2 mode (NTAG, Ultralight)")
    nfc_table.add_row("NFCType4", "0,U,N,B,D", "Type 4 mode (DESFire, ISO14443-4)")
    nfc_table.add_row("NFCType5", "0,U,N,B", "Type 5 mode (ICODE, ISO15693)")
    nfc_table.add_row("IgnoreRandomUID", "0,1", "Filter random UIDs")
    console.print(nfc_table)

    # DESFire Parameters
    console.print("\n[bold cyan]━━━ MIFARE DESFire Parameters ━━━[/bold cyan]")
    df_table = Table(show_header=True, header_style="bold")
    df_table.add_column("Parameter", style="cyan")
    df_table.add_column("Values")
    df_table.add_column("Description")
    df_table.add_row("DESFire#AppID", "Hex (6)", "Application ID")
    df_table.add_row("DESFire#FileID", "0-255", "File ID to read")
    df_table.add_row("DESFire#KeySlot", "1-9", "Key slot for auth")
    df_table.add_row("DESFire#Crypto", "0,1,3", "Crypto mode (0=None, 1=3DES, 3=AES)")
    console.print(df_table)

    # Keyboard Parameters
    console.print("\n[bold cyan]━━━ Keyboard Emulation Parameters ━━━[/bold cyan]")
    kb_table = Table(show_header=True, header_style="bold")
    kb_table.add_column("Parameter", style="cyan")
    kb_table.add_column("Values")
    kb_table.add_column("Description")
    kb_table.add_row("KBLogMode", "0,1", "Enable keyboard emulation")
    kb_table.add_row("KBSource", "Hex", "Data sources (A=Apple, G=Google, 2/4/5=NFC)")
    kb_table.add_row("KBPrefix", "String", "Prefix before data")
    kb_table.add_row("KBPostfix", "String", "Postfix after data (default: %0A)")
    kb_table.add_row("KBDelayMS", "5-255", "Delay between keystrokes (ms)")
    console.print(kb_table)

    # LED Parameters
    console.print("\n[bold cyan]━━━ LED Parameters ━━━[/bold cyan]")
    led_table = Table(show_header=True, header_style="bold")
    led_table.add_column("Parameter", style="cyan")
    led_table.add_column("Values")
    led_table.add_column("Description")
    led_table.add_row("LEDMode", "0-3", "LED mode (0=Off, 1=On, 2=Status, 3=Custom)")
    led_table.add_row("LEDSelect", "0-3", "LED type (0=External, 1/2=Onboard, 3=Serial)")
    led_table.add_row("PassLED", "Color,on,off,rep", "LED on successful read")
    led_table.add_row("PassErrorLED", "Color,on,off,rep", "LED on error")
    console.print(led_table)

    # Beep Parameters
    console.print("\n[bold cyan]━━━ Beep Parameters ━━━[/bold cyan]")
    beep_table = Table(show_header=True, header_style="bold")
    beep_table.add_column("Parameter", style="cyan")
    beep_table.add_column("Values")
    beep_table.add_column("Description")
    beep_table.add_row("PassBeep", "on,off,rep[,freq]", "Beep on successful read")
    beep_table.add_row("PassErrorBeep", "on,off,rep[,freq]", "Beep on error")
    beep_table.add_row("TagBeep", "on,off,rep[,freq]", "Beep on tag read")
    beep_table.add_row("StartBeep", "on,off,rep[,freq]", "Beep on startup")
    console.print(beep_table)

    console.print("\n[dim]Full documentation: docs/[/dim]")


@main.command()
@click.argument("filename", required=False, type=click.Path())
@click.option("--output", "-o", type=click.Path(), help="Output file")
def editor(filename: str | None, output: str | None) -> None:
    """Open the interactive TUI editor.

    Provides visual editing of VTAP100 configurations
    with context-sensitive help and live preview.

    Examples:
        vtap100 editor                  # New configuration
        vtap100 editor config.txt       # Open file
        vtap100 editor -o output.txt    # With output file
    """
    from vtap100.tui import run

    input_path = Path(filename) if filename else None
    output_path = Path(output) if output else input_path

    run(input_path=input_path, output_path=output_path)


if __name__ == "__main__":
    main()
