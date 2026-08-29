"""Keyboard emulation configuration form.

Form for editing keyboard emulation settings.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Switch
from vtap100.models.keyboard import KeyboardConfig
from vtap100.models.keyboard import build_kbsource_from_flags
from vtap100.models.keyboard import parse_kbsource_hex
from vtap100.tui.i18n import t
from vtap100.tui.widgets.forms.base import BaseConfigForm
from vtap100.tui.widgets.forms.base import ConfigChanged


class KeyboardConfigForm(BaseConfigForm):
    """Form for editing keyboard emulation configuration.

    This is a single-value section form (not a list like VAS/SmartTap).

    Fields:
    - log_mode: Enable keyboard emulation (switch)
    - source: Data sources for keyboard output
    - prefix: Optional prefix before data
    - postfix: Suffix after data
    - delay_ms: Delay between keystrokes

    Attributes:
        SECTION_NAME: Set to "keyboard".
        MESSAGE_TIMEOUT: Seconds before success messages auto-disappear.
    """

    SECTION_NAME = "keyboard"
    MESSAGE_TIMEOUT = 10.0

    DEFAULT_CSS = """
    KeyboardConfigForm {
        width: 100%;
        height: auto;
    }

    KeyboardConfigForm .form-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    KeyboardConfigForm .buttons {
        margin-top: 1;
        height: auto;
    }

    KeyboardConfigForm Button {
        margin-right: 1;
    }

    KeyboardConfigForm .error-message {
        color: $error;
        margin-top: 1;
    }

    KeyboardConfigForm .success-message {
        color: $success;
        margin-top: 1;
    }

    KeyboardConfigForm .field-row {
        height: auto;
        margin-bottom: 1;
    }

    KeyboardConfigForm .field-label {
        width: 20;
    }

    KeyboardConfigForm .field-section {
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }

    KeyboardConfigForm .bit-switches {
        margin-left: 2;
        padding: 1;
        border: solid $primary-darken-2;
        height: auto;
    }

    KeyboardConfigForm .bit-switches Label {
        margin-bottom: 0;
    }

    KeyboardConfigForm .bit-switches Switch {
        margin-bottom: 1;
    }

    KeyboardConfigForm .hex-display {
        color: $success;
        text-style: bold;
        margin-top: 1;
        padding: 0 1;
        background: $surface-darken-1;
        width: auto;
    }
    """

    def __init__(
        self,
        config: KeyboardConfig | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize the keyboard form.

        Args:
            config: Existing keyboard configuration to edit.
            id: Optional widget ID.
        """
        super().__init__(id=id)
        self._config = config or KeyboardConfig()

    def compose(self) -> ComposeResult:
        """Compose the keyboard form layout."""
        yield Label(t("sections.keyboard.title"), classes="form-title")

        # Log Mode (main enable switch)
        yield Label(t("forms.keyboard.enable"))
        yield Switch(value=self._config.log_mode, id="log_mode")

        # Source - Bitmask Switches
        yield Label(t("forms.keyboard.source_title"), classes="field-section")

        # Parse existing hex value into individual bits
        source_bits = parse_kbsource_hex(self._config.source)

        with Vertical(id="source-bits", classes="bit-switches"):
            yield Label(t("forms.keyboard.source_mobile_pass"))
            yield Switch(value=source_bits["mobile_pass"], id="source_mobile_pass")

            yield Label(t("forms.keyboard.source_stuid"))
            yield Switch(value=source_bits["stuid"], id="source_stuid")

            yield Label(t("forms.keyboard.source_card_emulation"))
            yield Switch(value=source_bits["card_emulation"], id="source_card_emulation")

            yield Label(t("forms.keyboard.source_scanners"))
            yield Switch(value=source_bits["scanners"], id="source_scanners")

            yield Label(t("forms.keyboard.source_command_interface"))
            yield Switch(value=source_bits["command_interface"], id="source_command_interface")

            yield Label(t("forms.keyboard.source_card_tag_uid"))
            yield Switch(value=source_bits["card_tag_uid"], id="source_card_tag_uid")

        # Live hex value display
        yield Label(
            t("forms.keyboard.source_hex_value", value=self._config.source),
            id="source_hex_display",
            classes="hex-display",
        )

        # Prefix
        yield Label(t("forms.keyboard.prefix"))
        yield Input(
            value=self._config.prefix or "",
            placeholder=t("forms.keyboard.prefix_placeholder"),
            id="prefix",
        )

        # Postfix
        yield Label(t("forms.keyboard.postfix"))
        yield Input(
            value=self._config.postfix or "",
            placeholder=t("forms.keyboard.postfix_placeholder"),
            id="postfix",
        )

        # Delay
        yield Label(t("forms.keyboard.delay_ms"))
        yield Input(
            value="" if self._config.delay_ms is None else str(self._config.delay_ms),
            placeholder=t("forms.keyboard.delay_ms_placeholder"),
            id="delay_ms",
        )

        with Horizontal(classes="buttons"):
            yield Button(t("common.buttons.save"), variant="success", id="save")

    def _get_source_value(self) -> str:
        """Calculate KBSource hex value from switch states.

        Returns:
            Hex string like "A5"
        """
        return build_kbsource_from_flags(
            mobile_pass=self.query_one("#source_mobile_pass", Switch).value,
            stuid=self.query_one("#source_stuid", Switch).value,
            card_emulation=self.query_one("#source_card_emulation", Switch).value,
            scanners=self.query_one("#source_scanners", Switch).value,
            command_interface=self.query_one("#source_command_interface", Switch).value,
            card_tag_uid=self.query_one("#source_card_tag_uid", Switch).value,
        )

    def get_config(self) -> KeyboardConfig:
        """Get the current configuration from form values.

        Returns:
            KeyboardConfig with current form values.
        """
        log_mode = self.query_one("#log_mode", Switch).value
        source = self._get_source_value()
        prefix_val = self.query_one("#prefix", Input).value
        prefix = prefix_val if prefix_val else None
        postfix_val = self.query_one("#postfix", Input).value
        postfix = postfix_val if postfix_val else None
        delay_str = self.query_one("#delay_ms", Input).value
        delay_ms = int(delay_str) if delay_str else None

        return KeyboardConfig(
            log_mode=log_mode,
            source=source,
            prefix=prefix,
            postfix=postfix,
            delay_ms=delay_ms,
        )

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch changes - update hex display if source bit changed.

        Args:
            event: The switch changed event.
        """
        # Call parent handler for ConfigChanged message
        super().on_switch_changed(event)

        # Update hex display if a source bit switch changed
        if event.switch.id and event.switch.id.startswith("source_"):
            hex_value = self._get_source_value()
            hex_label = self.query_one("#source_hex_display", Label)
            hex_label.update(t("forms.keyboard.source_hex_value", value=hex_value))

    def _clear_messages(self) -> None:
        """Clear previous validation errors and success messages from the form."""
        for error_label in self.query(".error-message"):
            error_label.remove()
        for success_label in self.query(".success-message"):
            success_label.remove()
        for input_widget in self.query(Input):
            input_widget.remove_class("invalid")

    def _show_success_message(self, message: str) -> None:
        """Show success message on the form.

        The message auto-disappears after MESSAGE_TIMEOUT seconds.

        Args:
            message: The success message to display.
        """
        label = Label(message, classes="success-message")
        self.mount(label)
        self.set_timer(self.MESSAGE_TIMEOUT, label.remove)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: The button pressed event.
        """
        self._clear_messages()

        if event.button.id == "save":
            try:
                config = self.get_config()
                self.app.config.keyboard = config
                self._show_success_message(t("common.messages.config_saved"))
                # Refresh preview
                self.post_message(
                    ConfigChanged(
                        section_id=self.SECTION_NAME,
                        field_name="saved",
                        value="",
                    )
                )
            except Exception as e:
                self.mount(
                    Label(t("common.messages.error", message=str(e)), classes="error-message")
                )
