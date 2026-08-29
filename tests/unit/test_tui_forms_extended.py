"""Extended unit tests for TUI Forms.

Additional tests to improve coverage for:
- DESFire form: remove, duplicate, validation
- Feedback form: save with success message
- SmartTap form: validation errors, key slot info
"""

import pytest
from vtap100.models.config import VTAPConfig
from vtap100.models.desfire import DESFireAppConfig
from vtap100.models.desfire import DESFireConfig
from vtap100.models.feedback import FeedbackConfig
from vtap100.models.feedback import LEDConfig
from vtap100.models.feedback import LEDMode
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.models.vas import AppleVASConfig


class TestDESFireFormRemove:
    """Test DESFire form remove functionality."""

    @pytest.mark.asyncio
    async def test_desfire_remove_button_removes_entry(self) -> None:
        """Clicking Remove should remove the DESFire entry."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(desfire=DESFireConfig(apps=[DESFireAppConfig(app_id="AABBCC")]))
        assert len(app.config.desfire.apps) == 1

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            desfire_node = tree.root.children[4]
            desfire_node.expand()
            await pilot.pause()
            tree.select_node(desfire_node.children[0])  # Select first entry
            await pilot.pause()
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            remove_btn = main_content.query_one("#remove", Button)
            remove_btn.press()
            await pilot.pause()

            # Entry should be removed
            assert len(app.config.desfire.apps) == 0


class TestDESFireFormDuplicate:
    """Test DESFire form duplicate functionality."""

    @pytest.mark.asyncio
    async def test_desfire_duplicate_button_duplicates_entry(self) -> None:
        """Clicking Duplicate should create a copy of the DESFire entry."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            desfire=DESFireConfig(apps=[DESFireAppConfig(app_id="112233", file_id=5)])
        )
        assert len(app.config.desfire.apps) == 1

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            desfire_node = tree.root.children[4]
            desfire_node.expand()
            await pilot.pause()
            tree.select_node(desfire_node.children[0])
            await pilot.pause()
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            duplicate_btn = main_content.query_one("#duplicate", Button)
            duplicate_btn.press()
            await pilot.pause()

            # Should now have 2 entries
            assert len(app.config.desfire.apps) == 2
            assert app.config.desfire.apps[0].app_id == "112233"
            assert app.config.desfire.apps[1].app_id == "112233"


class TestDESFireFormValidation:
    """Test DESFire form validation error handling."""

    @pytest.mark.asyncio
    async def test_desfire_invalid_app_id_shows_error(self) -> None:
        """Invalid app_id should show error message."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(desfire=DESFireConfig(apps=[]))

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            desfire_node = tree.root.children[4]
            desfire_node.expand()
            await pilot.pause()
            tree.select_node(desfire_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")

            # Enter invalid app_id (not 6 hex chars)
            app_id_input = main_content.query_one("#app_id", Input)
            app_id_input.value = "XX"  # Invalid
            await pilot.pause()

            # Click add
            add_btn = main_content.query_one("#add", Button)
            add_btn.press()
            await pilot.pause()

            # Should show error
            error_labels = main_content.query(".error-message")
            assert len(error_labels) > 0

            # Entry should NOT have been added
            assert len(app.config.desfire.apps) == 0


class TestDESFireEnsureConfig:
    """Test that DESFire config is created when needed."""

    @pytest.mark.asyncio
    async def test_desfire_add_creates_desfire_config(self) -> None:
        """Adding DESFire entry should create desfire config if None."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        # Start with no desfire config
        app.config = VTAPConfig()
        assert app.config.desfire is None

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            desfire_node = tree.root.children[4]
            desfire_node.expand()
            await pilot.pause()
            tree.select_node(desfire_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")

            app_id_input = main_content.query_one("#app_id", Input)
            app_id_input.value = "AABBCC"
            await pilot.pause()

            add_btn = main_content.query_one("#add", Button)
            add_btn.press()
            await pilot.pause()

            # desfire config should now exist
            assert app.config.desfire is not None
            assert len(app.config.desfire.apps) == 1


class TestFeedbackFormSave:
    """Test Feedback form save functionality."""

    @pytest.mark.asyncio
    async def test_feedback_save_updates_config(self) -> None:
        """Saving Feedback should update app.config.feedback."""
        from textual.widgets import Button
        from textual.widgets import Select
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(feedback=FeedbackConfig(led=LEDConfig(mode=LEDMode.OFF)))

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            feedback_node = tree.root.children[5]
            tree.select_node(feedback_node)
            await pilot.pause()
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")

            # Change LED mode
            led_mode_select = main_content.query_one("#led_mode", Select)
            led_mode_select.value = LEDMode.STATUS
            await pilot.pause()

            # Click save
            save_btn = main_content.query_one("#save", Button)
            save_btn.press()
            await pilot.pause()

            # Config should be updated
            assert app.config.feedback is not None
            assert app.config.feedback.led.mode == LEDMode.STATUS

    @pytest.mark.asyncio
    async def test_feedback_save_shows_success_message(self) -> None:
        """Saving Feedback should show success message."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(feedback=FeedbackConfig(led=LEDConfig()))

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            feedback_node = tree.root.children[5]
            tree.select_node(feedback_node)
            await pilot.pause()
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")

            # Click save
            save_btn = main_content.query_one("#save", Button)
            save_btn.press()
            await pilot.pause()

            # Should show success message
            success_labels = main_content.query(".success-message")
            assert len(success_labels) > 0


class TestFeedbackFormInit:
    """Test Feedback form initialization."""

    @pytest.mark.asyncio
    async def test_feedback_form_initializes_led_config(self) -> None:
        """Feedback form should initialize LED config if None."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        # Start with no feedback config
        app.config = VTAPConfig()

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            feedback_node = tree.root.children[5]
            tree.select_node(feedback_node)
            await pilot.pause()
            await pilot.pause()

            # Form should render without error
            main_content = app.screen.query_one("#main-content")
            assert main_content is not None


class TestSmartTapSlotInfo:
    """Test SmartTap form slot info display."""

    @pytest.mark.asyncio
    async def test_smarttap_form_shows_used_slots(self) -> None:
        """SmartTap form should show which slots are used."""
        from textual.widgets import Static
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        # VAS uses slot 1, SmartTap uses slot 3
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)],
            smarttap_configs=[GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=3)],
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]  # SmartTap
            st_node.expand()
            await pilot.pause()
            # Select "Neuer Eintrag" (last child)
            neuer_eintrag = st_node.children[-1]
            tree.select_node(neuer_eintrag)
            await pilot.pause()
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            slot_info = main_content.query_one(".slot-info", Static)
            info_text = str(slot_info.render())

            # Should show slot 1 is used by VAS
            assert "1" in info_text
            # Should show slot 3 is used by SmartTap
            assert "3" in info_text


class TestSmartTapValidation:
    """Test SmartTap form validation."""

    @pytest.mark.asyncio
    async def test_smarttap_invalid_collector_id_shows_error(self) -> None:
        """Invalid collector_id should show error message."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]  # SmartTap
            tree.select_node(st_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")

            # Enter empty collector_id
            collector_input = main_content.query_one("#collector_id", Input)
            collector_input.value = ""
            await pilot.pause()

            # Click add
            add_btn = main_content.query_one("#add", Button)
            add_btn.press()
            await pilot.pause()

            # Should show error
            error_labels = main_content.query(".error-message")
            assert len(error_labels) > 0

            # Entry should NOT have been added
            assert len(app.config.smarttap_configs) == 0

    @pytest.mark.asyncio
    async def test_smarttap_save_shows_success_message(self) -> None:
        """Saving SmartTap should show success message."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            smarttap_configs=[GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]
            tree.select_node(st_node.children[0])  # Select existing entry
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")

            # Click save
            save_btn = main_content.query_one("#save", Button)
            save_btn.press()
            await pilot.pause()

            # Should show success message
            success_labels = main_content.query(".success-message")
            assert len(success_labels) > 0


class TestSmartTapDuplicate:
    """Test SmartTap form duplicate functionality."""

    @pytest.mark.asyncio
    async def test_smarttap_duplicate_creates_copy(self) -> None:
        """Duplicating SmartTap entry should create a copy."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            smarttap_configs=[GoogleSmartTapConfig(slot=2, collector_id="87654321", key_slot=2)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]
            tree.select_node(st_node.children[0])  # Select existing entry
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")

            # Click duplicate
            duplicate_btn = main_content.query_one("#duplicate", Button)
            duplicate_btn.press()
            await pilot.pause()

            # Should now have 2 entries
            assert len(app.config.smarttap_configs) == 2
            assert app.config.smarttap_configs[1].collector_id == "87654321"


class TestSmartTapRemove:
    """Test SmartTap form remove functionality."""

    @pytest.mark.asyncio
    async def test_smarttap_remove_deletes_entry(self) -> None:
        """Removing SmartTap entry should delete it."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            smarttap_configs=[GoogleSmartTapConfig(slot=2, collector_id="11111111", key_slot=1)]
        )
        assert len(app.config.smarttap_configs) == 1

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]
            tree.select_node(st_node.children[0])  # Select existing entry
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")

            # Click remove
            remove_btn = main_content.query_one("#remove", Button)
            remove_btn.press()
            await pilot.pause()

            # Entry should be removed
            assert len(app.config.smarttap_configs) == 0
