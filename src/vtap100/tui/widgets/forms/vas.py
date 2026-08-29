"""Apple VAS configuration form.

Form for editing Apple VAS (Value Added Services) configurations.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Select
from textual.widgets import Static
from vtap100.models.vas import AppleVASConfig
from vtap100.tui.i18n import t
from vtap100.tui.widgets.forms.base import SlotBasedConfigForm


class VASConfigForm(SlotBasedConfigForm):
    """Form for editing Apple VAS configuration.

    Fields:
    - merchant_id: Pass Type ID (required, must start with 'pass.')
    - key_slot: Private key slot (1-6, required)
    - merchant_url: Optional URL

    Attributes:
        SECTION_NAME: Set to "vas".
        CONFIG_LIST_ATTR: Set to "vas_configs".
    """

    SECTION_NAME = "vas"
    CONFIG_LIST_ATTR = "vas_configs"

    DEFAULT_CSS = """
    VASConfigForm {
        width: 100%;
        height: auto;
    }

    VASConfigForm .form-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    VASConfigForm .buttons {
        margin-top: 1;
        height: auto;
    }

    VASConfigForm Button {
        margin-right: 1;
    }

    VASConfigForm .error-message {
        color: $error;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        config: AppleVASConfig | None = None,
        index: int = 0,
        is_new: bool = False,
        id: str | None = None,
    ) -> None:
        """Initialize the VAS form.

        Args:
            config: Existing VAS configuration to edit.
            index: Index in the vas_configs list.
            is_new: If True, this is a new config being created.
            id: Optional widget ID.
        """
        super().__init__(id=id)
        self.index = index
        self.is_new = is_new
        self._config = config or AppleVASConfig(slot=1, merchant_id="pass.", key_slot=1)

    def _get_used_key_slots(self) -> dict[int, str]:
        """Get key slots that are already in use by other configs.

        Returns:
            Dict mapping slot number to description (e.g., {1: "VAS #1", 3: "SmartTap #1"}).
            Excludes current config if editing.
        """
        used_slots: dict[int, str] = {}

        # Get all VAS config slots (except current if editing)
        for i, vas_config in enumerate(self.app.config.vas_configs):
            if not self.is_new and i == self.index:
                continue  # Skip current config when editing
            used_slots[vas_config.key_slot] = f"VAS #{i + 1}"

        # Get all SmartTap config slots
        for i, st_config in enumerate(self.app.config.smarttap_configs):
            used_slots[st_config.key_slot] = f"SmartTap #{i + 1}"

        return used_slots

    def compose(self) -> ComposeResult:
        """Compose the VAS form layout."""
        if self.is_new:
            title = t("sections.vas.new_title")
        else:
            title = t("sections.vas.edit_title", num=self.index + 1)
        yield Label(title, classes="form-title")

        yield Label(t("forms.vas.merchant_id"))
        yield Input(
            value=self._config.merchant_id,
            placeholder=t("forms.vas.merchant_id_placeholder"),
            id="merchant_id",
        )

        yield Label(t("forms.vas.key_slot"))
        # Generate options for Select: 1-6 (key_slot is now required, no more Auto/0)
        options = [(str(i), i) for i in range(1, 7)]
        yield Select(options, value=self._config.key_slot, id="key_slot")
        yield Static(self._get_slot_info_text(), classes="slot-info")

        yield Label(t("forms.vas.merchant_url"))
        yield Input(
            value=self._config.merchant_url or "",
            placeholder=t("forms.vas.merchant_url_placeholder"),
            id="merchant_url",
        )

        with Horizontal(classes="buttons"):
            if self.is_new:
                yield Button(t("common.buttons.add"), variant="success", id="add")
            else:
                yield Button(t("common.buttons.save"), variant="success", id="save")
                yield Button(t("common.buttons.duplicate"), variant="default", id="duplicate")
                yield Button(t("common.buttons.remove"), variant="error", id="remove")

    def get_config(self) -> AppleVASConfig:
        """Get the current configuration from form values.

        Returns:
            AppleVASConfig with current form values.
        """
        merchant_id = self.query_one("#merchant_id", Input).value
        select = self.query_one("#key_slot", Select)
        key_slot = select.value if select.value is not None else 1
        merchant_url = self.query_one("#merchant_url", Input).value or None

        return AppleVASConfig(
            slot=1,
            merchant_id=merchant_id,
            key_slot=key_slot,
            merchant_url=merchant_url,
        )
