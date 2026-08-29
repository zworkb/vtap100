"""MIFARE DESFire configuration form.

Form for editing DESFire application configurations.
"""

from pydantic import ValidationError
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import Checkbox
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Select
from vtap100.models.desfire import DESFireAppConfig
from vtap100.models.desfire import DESFireConfig
from vtap100.models.desfire import DESFireCryptoMode
from vtap100.models.desfire import DESFireDataFormat
from vtap100.models.desfire import DiversificationBuilder
from vtap100.tui.i18n import t
from vtap100.tui.widgets.forms.base import BaseConfigForm
from vtap100.tui.widgets.forms.base import ConfigAdded
from vtap100.tui.widgets.forms.base import ConfigChanged
from vtap100.tui.widgets.forms.base import ConfigRemoved


class DESFireConfigForm(BaseConfigForm):
    """Form for editing DESFire application configuration.

    Fields:
    - app_id: Application ID (6 hex characters, required)
    - file_id: File ID to read (1-255)
    - key_num: Key number for authentication
    - key_slot: Key slot (1-9)
    - crypto: Cryptographic mode (None/DES3/AES)
    - format: Data output format (Raw/KeyID v1/v2)
    - read_length: Number of bytes to read (1-255)
    - read_offset: Offset in file (0-255)
    - diversification: Enable key diversification

    Attributes:
        SECTION_NAME: Set to "desfire".
        MESSAGE_TIMEOUT: Seconds before success messages auto-disappear.
    """

    SECTION_NAME = "desfire"
    MESSAGE_TIMEOUT = 10.0

    DEFAULT_CSS = """
    DESFireConfigForm {
        width: 100%;
        height: auto;
    }

    DESFireConfigForm .form-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    DESFireConfigForm .form-row {
        height: auto;
        margin-bottom: 1;
    }

    DESFireConfigForm .form-row Label {
        width: 20;
        margin-right: 1;
    }

    DESFireConfigForm .form-row Input {
        width: 1fr;
    }

    DESFireConfigForm .form-row Select {
        width: 1fr;
    }

    DESFireConfigForm .form-row Checkbox {
        margin-left: 0;
    }

    DESFireConfigForm .buttons {
        margin-top: 1;
        height: auto;
    }

    DESFireConfigForm Button {
        margin-right: 1;
    }

    DESFireConfigForm .error-message {
        color: $error;
        margin-top: 1;
    }

    DESFireConfigForm .success-message {
        color: $success;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        config: DESFireAppConfig | None = None,
        index: int = 0,
        is_new: bool = False,
        id: str | None = None,
    ) -> None:
        """Initialize the DESFire form.

        Args:
            config: Existing DESFire app configuration to edit.
            index: Index in the desfire.apps list.
            is_new: If True, this is a new config being created.
            id: Optional widget ID.
        """
        super().__init__(id=id)
        self.index = index
        self.is_new = is_new
        self._config = config or DESFireAppConfig(app_id="000000")

    def compose(self) -> ComposeResult:
        """Compose the DESFire form layout."""
        if self.is_new:
            title = t("sections.desfire.new_title")
        else:
            title = t("sections.desfire.edit_title", num=self.index + 1)
        yield Label(title, classes="form-title")

        # App ID (required)
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.app_id"))
            yield Input(
                value=self._config.app_id,
                placeholder=t("forms.desfire.app_id_placeholder"),
                id="app_id",
            )

        # File ID
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.file_id"))
            yield Input(
                value=str(self._config.file_id) if self._config.file_id else "",
                placeholder=t("forms.desfire.file_id_placeholder"),
                id="file_id",
            )

        # Key Number
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.key_num"))
            yield Input(
                value=str(self._config.key_num) if self._config.key_num is not None else "",
                placeholder=t("forms.desfire.key_num_placeholder"),
                id="key_num",
            )

        # Key Slot
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.key_slot"))
            options: list[tuple[str, int | None]] = [(t("common.labels.not_set"), None)]
            options.extend([(str(i), i) for i in range(1, 10)])
            yield Select(options, value=self._config.key_slot, id="key_slot")

        # Crypto Mode
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.crypto"))
            crypto_options: list[tuple[str, DESFireCryptoMode | None]] = [
                (t("forms.desfire.crypto_none"), None),
                (t("forms.desfire.crypto_3des"), DESFireCryptoMode.DES3),
                (t("forms.desfire.crypto_aes"), DESFireCryptoMode.AES),
            ]
            yield Select(crypto_options, value=self._config.crypto, id="crypto")

        # Data Format
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.format"))
            format_options: list[tuple[str, DESFireDataFormat | None]] = [
                (t("forms.desfire.format_raw"), None),
                (t("forms.desfire.format_keyid_v1"), DESFireDataFormat.KEYID_V1),
                (t("forms.desfire.format_keyid_v2"), DESFireDataFormat.KEYID_V2),
            ]
            yield Select(format_options, value=self._config.format, id="format")

        # Read Length
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.read_length"))
            yield Input(
                value=str(self._config.read_length),
                placeholder=t("forms.desfire.read_length_placeholder"),
                id="read_length",
            )

        # Read Offset
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.read_offset"))
            yield Input(
                value=str(self._config.read_offset),
                placeholder=t("forms.desfire.read_offset_placeholder"),
                id="read_offset",
            )

        # Diversification
        with Horizontal(classes="form-row"):
            yield Label(t("forms.desfire.diversification"))
        current = self._config.diversification or 0
        with Horizontal(classes="form-row"):
            yield Checkbox(
                t("forms.desfire.diversification_active"),
                value=bool(current & DiversificationBuilder.ACTIVE),
                id="div_active",
            )
        with Horizontal(classes="form-row"):
            yield Checkbox(
                t("forms.desfire.diversification_omit_aid"),
                value=bool(current & DiversificationBuilder.OMIT_AID),
                id="div_omit_aid",
            )
        with Horizontal(classes="form-row"):
            yield Checkbox(
                t("forms.desfire.diversification_reverse_uid"),
                value=bool(current & DiversificationBuilder.REVERSE_UID),
                id="div_reverse_uid",
            )

        # Buttons
        with Horizontal(classes="buttons"):
            if self.is_new:
                yield Button(t("common.buttons.add"), variant="success", id="add")
            else:
                yield Button(t("common.buttons.save"), variant="success", id="save")
                yield Button(t("common.buttons.duplicate"), variant="default", id="duplicate")
                yield Button(t("common.buttons.remove"), variant="error", id="remove")

    def _ensure_desfire_config(self) -> None:
        """Ensure app.config.desfire exists."""
        if self.app.config.desfire is None:
            self.app.config.desfire = DESFireConfig(apps=[])

    def get_config(self) -> DESFireAppConfig:
        """Get the current configuration from form values.

        Returns:
            DESFireAppConfig with current form values.
        """
        app_id = self.query_one("#app_id", Input).value.strip().upper()

        # Parse optional integer fields
        file_id_str = self.query_one("#file_id", Input).value.strip()
        file_id = int(file_id_str) if file_id_str else None

        key_num_str = self.query_one("#key_num", Input).value.strip()
        key_num = int(key_num_str) if key_num_str else None

        key_slot_select = self.query_one("#key_slot", Select)
        key_slot = key_slot_select.value

        crypto_select = self.query_one("#crypto", Select)
        crypto = crypto_select.value

        format_select = self.query_one("#format", Select)
        data_format = format_select.value

        read_length_str = self.query_one("#read_length", Input).value.strip()
        read_length = int(read_length_str) if read_length_str else 3

        read_offset_str = self.query_one("#read_offset", Input).value.strip()
        read_offset = int(read_offset_str) if read_offset_str else 0

        builder = DiversificationBuilder()
        if self.query_one("#div_active", Checkbox).value:
            builder.active()
            if self.query_one("#div_omit_aid", Checkbox).value:
                builder.omit_aid()
            if self.query_one("#div_reverse_uid", Checkbox).value:
                builder.reverse_uid()
        diversification = builder.build() or None

        return DESFireAppConfig(
            app_id=app_id,
            file_id=file_id,
            key_num=key_num,
            key_slot=key_slot,
            crypto=crypto,
            format=data_format,
            read_length=read_length,
            read_offset=read_offset,
            diversification=diversification,
        )

    def _clear_messages(self) -> None:
        """Clear previous validation errors and success messages from the form."""
        for error_label in self.query(".error-message"):
            error_label.remove()
        for success_label in self.query(".success-message"):
            success_label.remove()
        for input_widget in self.query(Input):
            input_widget.remove_class("invalid")

    def _clear_errors(self) -> None:
        """Clear previous validation errors from the form."""
        self._clear_messages()

    def _show_validation_error(self, error: ValidationError) -> None:
        """Show validation error on the form.

        Args:
            error: The pydantic validation error.
        """
        for err in error.errors():
            field = err["loc"][0] if err["loc"] else None
            msg = err["msg"]
            if field:
                try:
                    input_widget = self.query_one(f"#{field}", Input)
                    input_widget.add_class("invalid")
                except Exception:
                    pass
            self.mount(Label(t("common.messages.error", message=msg), classes="error-message"))

    def _show_success_message(self, message: str) -> None:
        """Show success message on the form.

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
        self._clear_errors()

        if event.button.id == "add":
            try:
                config = self.get_config()
                self._ensure_desfire_config()
                self.app.config.desfire.apps.append(config)
                self.post_message(ConfigAdded(section_id=self.SECTION_NAME, index=self.index))
            except (ValidationError, ValueError) as e:
                if isinstance(e, ValidationError):
                    self._show_validation_error(e)
                else:
                    self.mount(
                        Label(t("common.messages.error", message=str(e)), classes="error-message")
                    )

        elif event.button.id == "save":
            try:
                config = self.get_config()
                self._ensure_desfire_config()
                self.app.config.desfire.apps[self.index] = config
                self._show_success_message(t("common.messages.config_saved"))
                # Refresh preview
                self.post_message(
                    ConfigChanged(
                        section_id=self.SECTION_NAME,
                        field_name="saved",
                        value="",
                    )
                )
            except (ValidationError, ValueError) as e:
                if isinstance(e, ValidationError):
                    self._show_validation_error(e)
                else:
                    self.mount(
                        Label(t("common.messages.error", message=str(e)), classes="error-message")
                    )

        elif event.button.id == "remove":
            self.app.config.desfire.apps.pop(self.index)
            self.post_message(ConfigRemoved(section_id=self.SECTION_NAME, index=self.index))

        elif event.button.id == "duplicate":
            try:
                config = self.get_config()
                self._ensure_desfire_config()
                self.app.config.desfire.apps.append(config)
                new_index = len(self.app.config.desfire.apps) - 1
                self.post_message(
                    ConfigAdded(section_id=self.SECTION_NAME, index=new_index, is_duplicate=True)
                )
            except (ValidationError, ValueError) as e:
                if isinstance(e, ValidationError):
                    self._show_validation_error(e)
                else:
                    self.mount(
                        Label(t("common.messages.error", message=str(e)), classes="error-message")
                    )
