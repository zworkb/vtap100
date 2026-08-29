"""Unit tests for TUI Forms - Phase 3.

Tests for:
- BaseConfigForm base class
- VASConfigForm for Apple VAS
- SmartTapConfigForm for Google Smart Tap
- Form validation and data binding
"""

import pytest
from vtap100.models.config import VTAPConfig
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.models.vas import AppleVASConfig


class TestFormsImports:
    """Test that form modules can be imported."""

    def test_import_base_form(self) -> None:
        """BaseConfigForm should be importable."""
        from vtap100.tui.widgets.forms.base import BaseConfigForm

        assert BaseConfigForm is not None

    def test_import_vas_form(self) -> None:
        """VASConfigForm should be importable."""
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        assert VASConfigForm is not None

    def test_import_smarttap_form(self) -> None:
        """SmartTapConfigForm should be importable."""
        from vtap100.tui.widgets.forms.smarttap import SmartTapConfigForm

        assert SmartTapConfigForm is not None

    def test_import_config_changed_message(self) -> None:
        """ConfigChanged message should be importable."""
        from vtap100.tui.widgets.forms.base import ConfigChanged

        assert ConfigChanged is not None


class TestBaseConfigForm:
    """Test BaseConfigForm base class."""

    def test_base_form_has_section_name(self) -> None:
        """BaseConfigForm should have SECTION_NAME attribute."""
        from vtap100.tui.widgets.forms.base import BaseConfigForm

        assert hasattr(BaseConfigForm, "SECTION_NAME")

    def test_base_form_is_abstract(self) -> None:
        """BaseConfigForm should be abstract-like (empty SECTION_NAME)."""
        from vtap100.tui.widgets.forms.base import BaseConfigForm

        assert BaseConfigForm.SECTION_NAME == ""


class TestVASConfigForm:
    """Test VASConfigForm widget."""

    def test_vas_form_section_name(self) -> None:
        """VASConfigForm should have 'vas' as SECTION_NAME."""
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        assert VASConfigForm.SECTION_NAME == "vas"

    def test_vas_form_creation_empty(self) -> None:
        """VASConfigForm can be created without config."""
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        form = VASConfigForm()
        assert form is not None

    def test_vas_form_creation_with_config(self) -> None:
        """VASConfigForm can be created with existing config."""
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        config = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        form = VASConfigForm(config=config, index=0)
        assert form._config == config
        assert form.index == 0


class TestVASConfigFormAsync:
    """Async tests for VASConfigForm."""

    @pytest.mark.asyncio
    async def test_vas_form_has_merchant_id_input(self) -> None:
        """VASConfigForm should have merchant_id input field."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp

        # Create app with VAS config
        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select VAS section to show form
            from textual.widgets import Tree

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]  # First node is VAS
            tree.select_node(vas_node.children[0])  # Select first VAS item
            await pilot.pause()

            # Check for merchant_id input
            main_content = app.screen.query_one("#main-content")
            inputs = main_content.query(Input)
            input_ids = [inp.id for inp in inputs]
            assert "merchant_id" in input_ids

    @pytest.mark.asyncio
    async def test_vas_form_has_key_slot_select(self) -> None:
        """VASConfigForm should have key_slot Select field."""
        from textual.widgets import Select
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            from textual.widgets import Tree

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            select = main_content.query_one("#key_slot", Select)
            assert select is not None

    @pytest.mark.asyncio
    async def test_vas_form_shows_correct_values(self) -> None:
        """VASConfigForm should display values from config."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.myapp", key_slot=2)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            from textual.widgets import Tree

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            assert merchant_input.value == "pass.com.example.myapp"


class TestFormFocus:
    """Test that form fields get focus when selecting tree entries."""

    @pytest.mark.asyncio
    async def test_selecting_vas_entry_focuses_first_field(self) -> None:
        """Selecting a VAS entry should focus the first form field."""
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # Select #1 entry
            await pilot.pause()

            # First input field (merchant_id) should have focus
            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            assert merchant_input.has_focus

    @pytest.mark.asyncio
    async def test_selecting_smarttap_entry_focuses_first_field(self) -> None:
        """Selecting a SmartTap entry should focus the first form field."""
        from textual.widgets import Input
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
            st_node = tree.root.children[1]  # SmartTap is second node
            tree.select_node(st_node.children[0])  # Select #1 entry
            await pilot.pause()

            # First input field (collector_id) should have focus
            main_content = app.screen.query_one("#main-content")
            collector_input = main_content.query_one("#collector_id", Input)
            assert collector_input.has_focus

    @pytest.mark.asyncio
    async def test_selecting_neuer_eintrag_focuses_first_field(self) -> None:
        """Selecting 'Neuer Eintrag' should focus the first form field."""
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            # First input field (merchant_id) should have focus
            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            assert merchant_input.has_focus


class TestSmartTapConfigForm:
    """Test SmartTapConfigForm widget."""

    def test_smarttap_form_section_name(self) -> None:
        """SmartTapConfigForm should have 'smarttap' as SECTION_NAME."""
        from vtap100.tui.widgets.forms.smarttap import SmartTapConfigForm

        assert SmartTapConfigForm.SECTION_NAME == "smarttap"

    def test_smarttap_form_creation_with_config(self) -> None:
        """SmartTapConfigForm can be created with existing config."""
        from vtap100.tui.widgets.forms.smarttap import SmartTapConfigForm

        config = GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=1, key_version=1)
        form = SmartTapConfigForm(config=config, index=0)
        assert form._config == config


class TestSmartTapConfigFormAsync:
    """Async tests for SmartTapConfigForm."""

    @pytest.mark.asyncio
    async def test_smarttap_form_has_collector_id_input(self) -> None:
        """SmartTapConfigForm should have collector_id input field."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            smarttap_configs=[
                GoogleSmartTapConfig(slot=2, collector_id="96972794", key_slot=1, key_version=1)
            ]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            from textual.widgets import Tree

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]  # Second node is SmartTap
            tree.select_node(st_node.children[0])  # Select first ST item
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            inputs = main_content.query(Input)
            input_ids = [inp.id for inp in inputs]
            assert "collector_id" in input_ids


class TestAddNewConfig:
    """Test adding new configurations."""

    @pytest.mark.asyncio
    async def test_clicking_neuer_eintrag_shows_new_form(self) -> None:
        """Clicking 'Neuer Eintrag' should show new config form."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        # Start with empty config

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]  # Apple VAS section
            # Click on "Neuer Eintrag" child (first child when empty)
            neuer_eintrag = vas_node.children[0]
            tree.select_node(neuer_eintrag)
            await pilot.pause()

            # Should show form with "Hinzufügen" button
            main_content = app.screen.query_one("#main-content")
            buttons = main_content.query(Button)
            button_ids = [btn.id for btn in buttons]
            assert "add" in button_ids

    @pytest.mark.asyncio
    async def test_new_vas_form_shows_correct_title(self) -> None:
        """New VAS form should show 'Neue Apple VAS Konfiguration' title."""
        from textual.widgets import Label
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            # Click on "Neuer Eintrag"
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            title_label = main_content.query_one(".form-title", Label)
            # Use render() to get the label text
            label_text = title_label.render()
            assert "Neue" in str(label_text)

    @pytest.mark.asyncio
    async def test_existing_vas_form_has_remove_button(self) -> None:
        """Existing VAS form should have remove button, not add."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # Select existing item
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            buttons = main_content.query(Button)
            button_ids = [btn.id for btn in buttons]
            assert "remove" in button_ids
            assert "add" not in button_ids

    @pytest.mark.asyncio
    async def test_clicking_add_button_adds_vas_config(self) -> None:
        """Clicking Add button should add new VAS config to app.config."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        assert len(app.config.vas_configs) == 0  # Start empty

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select "Neuer Eintrag" to show new form
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            # Fill in the merchant_id field
            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.newapp"
            await pilot.pause()

            # Click the Add button
            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Config should now have one VAS entry
            assert len(app.config.vas_configs) == 1
            assert app.config.vas_configs[0].merchant_id == "pass.com.example.newapp"

    @pytest.mark.asyncio
    async def test_clicking_add_button_refreshes_sidebar(self) -> None:
        """After adding, sidebar should show new item."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]

            # Initially only "Neuer Eintrag" child
            assert len(vas_node.children) == 1

            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            # Fill form and click Add
            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.test"
            await pilot.pause()

            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Re-query the tree (it was rebuilt after refresh)
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]

            # Sidebar should now have 2 children: #1 entry + "Neuer Eintrag"
            assert len(vas_node.children) == 2

    @pytest.mark.asyncio
    async def test_clicking_add_button_adds_smarttap_config(self) -> None:
        """Clicking Add button should add new SmartTap config to app.config."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        assert len(app.config.smarttap_configs) == 0  # Start empty

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select SmartTap "Neuer Eintrag" to show new form
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]  # Second node is SmartTap
            tree.select_node(st_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            # Fill in the collector_id field
            main_content = app.screen.query_one("#main-content")
            collector_input = main_content.query_one("#collector_id", Input)
            collector_input.value = "12345678"
            await pilot.pause()

            # Click the Add button
            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Config should now have one SmartTap entry
            assert len(app.config.smarttap_configs) == 1
            assert app.config.smarttap_configs[0].collector_id == "12345678"

    @pytest.mark.asyncio
    async def test_clicking_neuer_eintrag_twice_does_not_error(self) -> None:
        """Clicking 'Neuer Eintrag' twice should not cause duplicate ID error."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            neuer_eintrag = vas_node.children[0]

            # Click "Neuer Eintrag" first time
            tree.select_node(neuer_eintrag)
            await pilot.pause()

            # Click "Neuer Eintrag" second time - should not error
            tree.select_node(neuer_eintrag)
            await pilot.pause()

            # Form should still be displayed
            main_content = app.screen.query_one("#main-content")
            assert main_content.query_one("#merchant_id") is not None


class TestExistingConfigButtons:
    """Test buttons for existing configurations (Save, Remove, Duplicate)."""

    @pytest.mark.asyncio
    async def test_existing_vas_form_has_save_button(self) -> None:
        """Existing VAS form should have a save button."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            buttons = main_content.query(Button)
            button_ids = [btn.id for btn in buttons]
            assert "save" in button_ids

    @pytest.mark.asyncio
    async def test_clicking_save_button_updates_config(self) -> None:
        """Clicking Save should update the config with form values."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.original", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            # Change the merchant_id
            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.updated"
            await pilot.pause()

            # Click Save
            save_button = main_content.query_one("#save", Button)
            save_button.press()
            await pilot.pause()

            # Config should be updated
            assert app.config.vas_configs[0].merchant_id == "pass.com.updated"

    @pytest.mark.asyncio
    async def test_clicking_remove_button_removes_config(self) -> None:
        """Clicking Remove should remove the config from the list."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )
        assert len(app.config.vas_configs) == 1

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            # Click Remove
            main_content = app.screen.query_one("#main-content")
            remove_button = main_content.query_one("#remove", Button)
            remove_button.press()
            await pilot.pause()

            # Config should be removed
            assert len(app.config.vas_configs) == 0

    @pytest.mark.asyncio
    async def test_clicking_remove_refreshes_sidebar(self) -> None:
        """After removing, sidebar should update."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            # 2 children: #1 entry + "Neuer Eintrag"
            assert len(vas_node.children) == 2

            tree.select_node(vas_node.children[0])  # Select #1 entry
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            remove_button = main_content.query_one("#remove", Button)
            remove_button.press()
            await pilot.pause()

            # Re-query tree after refresh
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            # After removal, only "Neuer Eintrag" remains
            assert len(vas_node.children) == 1

    @pytest.mark.asyncio
    async def test_after_remove_section_stays_expanded(self) -> None:
        """After removing, the section node should stay expanded."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # Select #1 entry
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            remove_button = main_content.query_one("#remove", Button)
            remove_button.press()
            await pilot.pause()

            # Re-query tree after refresh
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]

            # VAS node should still be expanded
            assert vas_node.is_expanded

            # Cursor should be on VAS section node itself (not on keyboard or children)
            cursor = tree.cursor_node
            assert cursor is not None
            assert cursor.data == "vas", f"Expected cursor on 'vas', got '{cursor.data}'"

    @pytest.mark.asyncio
    async def test_after_remove_smarttap_section_stays_expanded(self) -> None:
        """After removing SmartTap, the section node should stay expanded."""
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
            st_node = tree.root.children[1]  # SmartTap is second node
            tree.select_node(st_node.children[0])  # Select #1 entry
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            remove_button = main_content.query_one("#remove", Button)
            remove_button.press()
            await pilot.pause()

            # Re-query tree after refresh
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]

            # SmartTap node should still be expanded
            assert st_node.is_expanded

            # Cursor should be on SmartTap section node itself (not on keyboard or children)
            cursor = tree.cursor_node
            assert cursor is not None
            assert cursor.data == "smarttap", f"Expected cursor on 'smarttap', got '{cursor.data}'"

    @pytest.mark.asyncio
    async def test_clicking_duplicate_button_duplicates_config(self) -> None:
        """Clicking Duplicate should create a copy of the config."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.original", key_slot=2)]
        )
        assert len(app.config.vas_configs) == 1

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            # Click Duplicate
            main_content = app.screen.query_one("#main-content")
            duplicate_button = main_content.query_one("#duplicate", Button)
            duplicate_button.press()
            await pilot.pause()

            # Should now have 2 configs
            assert len(app.config.vas_configs) == 2
            # Both should have same values
            assert app.config.vas_configs[0].merchant_id == "pass.com.original"
            assert app.config.vas_configs[1].merchant_id == "pass.com.original"
            assert app.config.vas_configs[1].key_slot == 2


class TestValidationErrorHandling:
    """Test that validation errors are handled gracefully."""

    @pytest.mark.asyncio
    async def test_invalid_vas_merchant_id_shows_error(self) -> None:
        """Invalid merchant_id should show error, not crash."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select "Neuer Eintrag"
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            # Enter invalid merchant_id (doesn't start with 'pass.')
            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "invalid_id"
            await pilot.pause()

            # Click Add - should NOT crash
            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Config should NOT have been added
            assert len(app.config.vas_configs) == 0

            # Input should have error class
            assert merchant_input.has_class("invalid")

    @pytest.mark.asyncio
    async def test_invalid_vas_shows_error_message(self) -> None:
        """Invalid input should show error message label."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "invalid"
            await pilot.pause()

            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Should show error label
            error_labels = main_content.query(".error-message")
            assert len(error_labels) > 0


class TestPostAddBehavior:
    """Test behavior after successfully adding a new configuration."""

    @pytest.mark.asyncio
    async def test_after_add_switches_to_edit_view(self) -> None:
        """After adding, should switch to edit view of new entry."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select "Neuer Eintrag" to show new form
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            # Fill form and add
            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.new"
            await pilot.pause()

            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Should now show edit view (with save/remove/duplicate buttons, not add)
            buttons = main_content.query(Button)
            button_ids = [btn.id for btn in buttons]
            assert "save" in button_ids
            assert "remove" in button_ids
            assert "add" not in button_ids

    @pytest.mark.asyncio
    async def test_after_add_shows_success_message(self) -> None:
        """After adding, should show success message."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.success"
            await pilot.pause()

            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Should show success message
            success_labels = main_content.query(".success-message")
            assert len(success_labels) > 0
            # Message should contain section type
            success_text = str(success_labels[0].render())
            assert "VAS" in success_text
            assert "angelegt" in success_text

    @pytest.mark.asyncio
    async def test_after_smarttap_add_shows_correct_message(self) -> None:
        """After adding SmartTap, should show SmartTap success message."""
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
            collector_input = main_content.query_one("#collector_id", Input)
            collector_input.value = "12345678"
            await pilot.pause()

            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Should show success message for SmartTap
            success_labels = main_content.query(".success-message")
            assert len(success_labels) > 0
            success_text = str(success_labels[0].render())
            assert "Smart Tap" in success_text
            assert "angelegt" in success_text

    @pytest.mark.asyncio
    async def test_save_button_shows_success_message(self) -> None:
        """Clicking Save should show a success message."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.original", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # Select existing entry
            await pilot.pause()

            # Change the merchant_id
            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.updated"
            await pilot.pause()

            # Click Save
            save_button = main_content.query_one("#save", Button)
            save_button.press()
            await pilot.pause()

            # Should show success message
            success_labels = main_content.query(".success-message")
            assert len(success_labels) > 0
            success_text = str(success_labels[0].render())
            assert "gespeichert" in success_text

    @pytest.mark.asyncio
    async def test_duplicate_button_shows_success_message(self) -> None:
        """Clicking Duplicate should show 'dupliziert' message."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.original", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # Select existing entry
            await pilot.pause()

            # Click Duplicate
            main_content = app.screen.query_one("#main-content")
            duplicate_button = main_content.query_one("#duplicate", Button)
            duplicate_button.press()
            await pilot.pause()

            # Should show "dupliziert" message, not "angelegt"
            success_labels = main_content.query(".success-message")
            assert len(success_labels) > 0
            success_text = str(success_labels[0].render())
            assert "dupliziert" in success_text
            assert "VAS" in success_text

    @pytest.mark.asyncio
    async def test_add_success_message_clears_on_save(self) -> None:
        """The 'angelegt' message should clear when clicking Save."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            # Add a new VAS config
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.test"
            await pilot.pause()

            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # "angelegt" message should be shown
            success_labels = main_content.query(".success-message")
            assert len(success_labels) > 0
            assert "angelegt" in str(success_labels[0].render())

            # Now click Save
            save_button = main_content.query_one("#save", Button)
            save_button.press()
            await pilot.pause()

            # "angelegt" message should be gone, only "gespeichert" should remain
            success_labels = main_content.query(".success-message")
            assert len(success_labels) == 1
            success_text = str(success_labels[0].render())
            assert "gespeichert" in success_text
            assert "angelegt" not in success_text

    @pytest.mark.asyncio
    async def test_after_add_tree_node_is_selected(self) -> None:
        """After adding, the new entry should be selected in the tree."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            # Add a new VAS config
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # "Neuer Eintrag"
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            merchant_input = main_content.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.test"
            await pilot.pause()

            add_button = main_content.query_one("#add", Button)
            add_button.press()
            await pilot.pause()

            # Re-query tree after refresh
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]

            # VAS node should be expanded
            assert vas_node.is_expanded

            # The new entry (#1) should be selected
            selected = tree.cursor_node
            assert selected is not None
            assert selected.data == "vas:0"

    @pytest.mark.asyncio
    async def test_after_duplicate_tree_node_is_selected(self) -> None:
        """After duplicating, the new entry should be selected in the tree."""
        from textual.widgets import Button
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.original", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])  # Select #1
            await pilot.pause()

            # Click Duplicate
            main_content = app.screen.query_one("#main-content")
            duplicate_button = main_content.query_one("#duplicate", Button)
            duplicate_button.press()
            await pilot.pause()

            # Re-query tree after refresh
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]

            # VAS node should be expanded
            assert vas_node.is_expanded

            # The duplicated entry (#2) should be selected
            selected = tree.cursor_node
            assert selected is not None
            assert selected.data == "vas:1"  # Second entry (index 1)

    @pytest.mark.asyncio
    async def test_success_message_auto_disappears(self) -> None:
        """Success message should auto-disappear after timeout."""
        from textual.widgets import Button
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        # Set shorter timeout for testing
        original_timeout = VASConfigForm.MESSAGE_TIMEOUT
        VASConfigForm.MESSAGE_TIMEOUT = 0.1

        try:
            app = VTAPEditorApp()
            app.config = VTAPConfig(
                vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.original", key_slot=1)]
            )

            async with app.run_test() as pilot:
                await pilot.pause()

                sidebar = app.screen.query_one("#sidebar")
                tree = sidebar.query_one(Tree)
                vas_node = tree.root.children[0]
                tree.select_node(vas_node.children[0])
                await pilot.pause()

                main_content = app.screen.query_one("#main-content")
                merchant_input = main_content.query_one("#merchant_id", Input)
                merchant_input.value = "pass.com.updated"
                await pilot.pause()

                # Click Save
                save_button = main_content.query_one("#save", Button)
                save_button.press()
                await pilot.pause()

                # Message should be visible immediately
                success_labels = main_content.query(".success-message")
                assert len(success_labels) == 1

                # Wait for auto-disappear
                import asyncio

                await asyncio.sleep(0.15)
                await pilot.pause()

                # Message should be gone
                success_labels = main_content.query(".success-message")
                assert len(success_labels) == 0
        finally:
            # Restore original timeout
            VASConfigForm.MESSAGE_TIMEOUT = original_timeout


class TestKeySlotSelect:
    """Test that key_slot uses Select with info text showing slot usage."""

    @pytest.mark.asyncio
    async def test_vas_form_uses_select_for_key_slot(self) -> None:
        """VAS form should use Select for key_slot."""
        from textual.widgets import Select
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            # Should have Select for key_slot
            select = main_content.query_one("#key_slot", Select)
            assert select is not None

    @pytest.mark.asyncio
    async def test_smarttap_form_uses_select_for_key_slot(self) -> None:
        """SmartTap form should use Select for key_slot."""
        from textual.widgets import Select
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            smarttap_configs=[GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=2)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]  # SmartTap is second
            tree.select_node(st_node.children[0])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            # Should have Select for key_slot
            select = main_content.query_one("#key_slot", Select)
            assert select is not None

    @pytest.mark.asyncio
    async def test_vas_select_has_6_options(self) -> None:
        """VAS key_slot Select should have 6 options (1-6, no Auto/0)."""
        from textual.widgets import Select
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            select = main_content.query_one("#key_slot", Select)
            # Count options by checking the _options property
            # Select includes a blank option by default: 7 total (1 blank + 6 slots)
            options = list(select._options)
            # Filter out blank option to count actual slot options
            slot_options = [opt for opt in options if opt[1] != Select.BLANK]
            assert len(slot_options) == 6

    @pytest.mark.asyncio
    async def test_correct_slot_is_selected(self) -> None:
        """The current config's key_slot should be selected in Select."""
        from textual.widgets import Select
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=3)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            select = main_content.query_one("#key_slot", Select)

            # Slot 3 should be selected
            assert select.value == 3

    @pytest.mark.asyncio
    async def test_vas_form_shows_slot_info_text(self) -> None:
        """VAS form should show info text about slot usage below Select."""
        from textual.widgets import Static
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        # VAS config uses slot 1, SmartTap uses slot 3
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)],
            smarttap_configs=[GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=3)],
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Open new VAS form
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            # Click "Neuer Eintrag" (second child, after #1)
            tree.select_node(vas_node.children[1])
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            # Should have Static with slot-info class showing used/free slots
            slot_info = main_content.query_one(".slot-info", Static)
            info_text = str(slot_info.render())

            # Should show which slots are used
            assert "Belegt:" in info_text or "belegt" in info_text.lower()
            assert "1" in info_text  # Slot 1 is used
            assert "3" in info_text  # Slot 3 is used

    @pytest.mark.asyncio
    async def test_slot_info_shows_free_slots(self) -> None:
        """Slot info should show which slots are free."""
        from textual.widgets import Static
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        # Only slot 1 is used
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Open new VAS form
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[1])  # "Neuer Eintrag"
            await pilot.pause()

            main_content = app.screen.query_one("#main-content")
            slot_info = main_content.query_one(".slot-info", Static)
            info_text = str(slot_info.render())

            # Should show which slots are free
            assert "Frei:" in info_text or "frei" in info_text.lower()


class TestSidebarTreeLabels:
    """Test that sidebar shows merchant_id/collector_id with slot info."""

    @pytest.mark.asyncio
    async def test_vas_tree_shows_merchant_id(self) -> None:
        """VAS tree entry should show merchant_id instead of #1."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.myapp", key_slot=2)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]

            # First child should show merchant_id
            entry_node = vas_node.children[0]
            label = str(entry_node.label)
            assert "pass.com.example.myapp" in label
            # Should NOT show just "#1"
            assert label != "#1"

    @pytest.mark.asyncio
    async def test_smarttap_tree_shows_collector_id(self) -> None:
        """SmartTap tree entry should show collector_id instead of #1."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            smarttap_configs=[GoogleSmartTapConfig(slot=2, collector_id="96972794", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            st_node = tree.root.children[1]  # SmartTap is second

            # First child should show collector_id
            entry_node = st_node.children[0]
            label = str(entry_node.label)
            assert "96972794" in label
            # Should NOT show just "#1"
            assert label != "#1"

    @pytest.mark.asyncio
    async def test_vas_tree_shows_slot_info(self) -> None:
        """VAS tree entry should show slot info (Slot X or Auto)."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=3)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]

            entry_node = vas_node.children[0]
            label = str(entry_node.label)
            # Should show slot 3
            assert "3" in label or "Slot 3" in label

    @pytest.mark.asyncio
    async def test_vas_tree_shows_slot_number(self) -> None:
        """VAS tree entry should show slot number (1-6)."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=2)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]

            entry_node = vas_node.children[0]
            label = str(entry_node.label)
            # Should show slot number 2
            assert "2" in label
