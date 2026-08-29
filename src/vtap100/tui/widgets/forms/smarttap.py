"""Google Smart Tap configuration form.

Form for editing Google Smart Tap configurations.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Select
from textual.widgets import Static
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.tui.i18n import t
from vtap100.tui.widgets.forms.base import SlotBasedConfigForm


class SmartTapConfigForm(SlotBasedConfigForm):
    """Form for editing Google Smart Tap configuration.

    Fields:
    - collector_id: Google Collector ID (required)
    - key_slot: Private key slot (1-6, required)
    - key_version: Key version number

    Attributes:
        SECTION_NAME: Set to "smarttap".
        CONFIG_LIST_ATTR: Set to "smarttap_configs".
    """

    SECTION_NAME = "smarttap"
    CONFIG_LIST_ATTR = "smarttap_configs"

    DEFAULT_CSS = """
    SmartTapConfigForm {
        width: 100%;
        height: auto;
    }

    SmartTapConfigForm .form-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    SmartTapConfigForm .buttons {
        margin-top: 1;
        height: auto;
    }

    SmartTapConfigForm Button {
        margin-right: 1;
    }

    SmartTapConfigForm .error-message {
        color: $error;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        config: GoogleSmartTapConfig | None = None,
        index: int = 0,
        is_new: bool = False,
        id: str | None = None,
    ) -> None:
        """Initialize the Smart Tap form.

        Args:
            config: Existing Smart Tap configuration to edit.
            index: Index in the smarttap_configs list.
            is_new: If True, this is a new config being created.
            id: Optional widget ID.
        """
        super().__init__(id=id)
        self.index = index
        self.is_new = is_new
        # Use placeholder collector_id and key_slot=1 for new configs
        self._config = config or GoogleSmartTapConfig(slot=2, collector_id="00000000", key_slot=1)

    def _get_used_key_slots(self) -> dict[int, str]:
        """Get key slots that are already in use by other configs.

        Returns:
            Dict mapping slot number to description (e.g., {1: "VAS #1", 3: "SmartTap #1"}).
            Excludes current config if editing.
        """
        used_slots: dict[int, str] = {}

        # Get all VAS config slots
        for i, vas_config in enumerate(self.app.config.vas_configs):
            used_slots[vas_config.key_slot] = f"VAS #{i + 1}"

        # Get all SmartTap config slots (except current if editing)
        for i, st_config in enumerate(self.app.config.smarttap_configs):
            if not self.is_new and i == self.index:
                continue  # Skip current config when editing
            used_slots[st_config.key_slot] = f"SmartTap #{i + 1}"

        return used_slots

    def compose(self) -> ComposeResult:
        """Compose the Smart Tap form layout."""
        if self.is_new:
            title = t("sections.smarttap.new_title")
        else:
            title = t("sections.smarttap.edit_title", num=self.index + 1)
        yield Label(title, classes="form-title")

        yield Label(t("forms.smarttap.collector_id"))
        yield Input(
            value=self._config.collector_id,
            placeholder=t("forms.smarttap.collector_id_placeholder"),
            id="collector_id",
        )

        yield Label(t("forms.smarttap.key_slot"))
        # Generate options for Select: 1-6 (key_slot is now required, no more Auto/0)
        options = [(str(i), i) for i in range(1, 7)]
        yield Select(options, value=self._config.key_slot, id="key_slot")
        yield Static(self._get_slot_info_text(), classes="slot-info")

        yield Label(t("forms.smarttap.key_version"))
        yield Input(
            value=str(self._config.key_version) if self._config.key_version else "",
            placeholder="1",
            id="key_version",
        )

        with Horizontal(classes="buttons"):
            if self.is_new:
                yield Button(t("common.buttons.add"), variant="success", id="add")
            else:
                yield Button(t("common.buttons.save"), variant="success", id="save")
                yield Button(t("common.buttons.duplicate"), variant="default", id="duplicate")
                yield Button(t("common.buttons.remove"), variant="error", id="remove")

    def get_config(self) -> GoogleSmartTapConfig:
        """Get the current configuration from form values.

        Returns:
            GoogleSmartTapConfig with current form values.
        """
        collector_id = self.query_one("#collector_id", Input).value
        select = self.query_one("#key_slot", Select)
        key_slot = select.value if select.value is not None else 1
        key_version_str = self.query_one("#key_version", Input).value
        key_version = int(key_version_str) if key_version_str else 0

        return GoogleSmartTapConfig(
            slot=2,
            collector_id=collector_id,
            key_slot=key_slot,
            key_version=key_version,
        )
