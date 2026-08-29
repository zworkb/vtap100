"""Unit tests for navigation interception with dirty form detection.

TDD Red Phase: These tests define the expected behavior of the
navigation interception when there are unsaved changes.
"""

import pytest
from vtap100.models.config import VTAPConfig
from vtap100.models.vas import AppleVASConfig


class TestNavigationWithNewForm:
    """Tests for navigation behavior with new (unsaved) forms."""

    @pytest.mark.asyncio
    async def test_new_form_save_adds_entry(self) -> None:
        """Clicking Save on dialog for a new form should add the entry."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.editor import EditorScreen
        from vtap100.tui.screens.unsaved_changes_dialog import UnsavedChangesDialog
        from vtap100.tui.widgets.forms.vas import VASConfigForm
        from vtap100.tui.widgets.sidebar import SectionSelected

        app = VTAPEditorApp()
        # Start with empty config
        app.config = VTAPConfig(vas_configs=[])

        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to add new VAS (index=None means new)
            app.screen.post_message(SectionSelected(section_id="vas", index=None))
            await pilot.pause()

            # Fill in data to make form dirty
            form = app.screen.query_one(VASConfigForm)
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.newentry"
            await pilot.pause()

            # Verify form is dirty
            assert form.is_dirty is True

            # Try to navigate away
            app.screen.post_message(SectionSelected(section_id="keyboard", index=None))
            await pilot.pause()

            # Dialog should show
            assert isinstance(app.screen, UnsavedChangesDialog)

            # Click Save (should add the new entry)
            await pilot.click("#save-btn")
            await pilot.pause()

            # Should be back to editor
            assert isinstance(app.screen, EditorScreen)

            # New entry should have been added to config
            assert len(app.config.vas_configs) == 1
            assert app.config.vas_configs[0].merchant_id == "pass.com.example.newentry"

    @pytest.mark.asyncio
    async def test_dialog_shows_add_button_for_new_forms(self) -> None:
        """Dialog should show 'Add' instead of 'Save' for new forms."""
        from textual.widgets import Button
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.unsaved_changes_dialog import UnsavedChangesDialog
        from vtap100.tui.widgets.forms.vas import VASConfigForm
        from vtap100.tui.widgets.sidebar import SectionSelected

        app = VTAPEditorApp()
        app.config = VTAPConfig(vas_configs=[])

        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to add new VAS
            app.screen.post_message(SectionSelected(section_id="vas", index=None))
            await pilot.pause()

            # Fill in data
            form = app.screen.query_one(VASConfigForm)
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.test"
            await pilot.pause()

            # Try to navigate away
            app.screen.post_message(SectionSelected(section_id="keyboard", index=None))
            await pilot.pause()

            # Dialog should show with "Add" button
            assert isinstance(app.screen, UnsavedChangesDialog)
            save_btn = app.screen.query_one("#save-btn", Button)
            # Button label should be "Add" (or German "Hinzufügen")
            assert save_btn.label in ("Add", "Hinzufügen")


class TestNavigationWithDirtyForm:
    """Tests for navigation behavior when form has unsaved changes."""

    @pytest.mark.asyncio
    async def test_navigation_without_changes_proceeds_immediately(self) -> None:
        """Navigation without unsaved changes should proceed immediately."""
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.widgets.sidebar import SectionSelected

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to VAS (will show new form)
            app.screen.post_message(SectionSelected(section_id="vas", index=None))
            await pilot.pause()

            # Without making changes, navigate to keyboard
            app.screen.post_message(SectionSelected(section_id="keyboard", index=None))
            await pilot.pause()

            # Should be on keyboard form now (no dialog shown)
            # The screen should still be EditorScreen, not a dialog
            from vtap100.tui.screens.editor import EditorScreen

            assert isinstance(app.screen, EditorScreen)

    @pytest.mark.asyncio
    async def test_navigation_with_dirty_form_shows_dialog(self) -> None:
        """Navigation with unsaved changes should show dialog."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.unsaved_changes_dialog import UnsavedChangesDialog
        from vtap100.tui.widgets.forms.vas import VASConfigForm
        from vtap100.tui.widgets.sidebar import SectionSelected

        # Create app with an existing VAS config
        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to VAS #1 (edit existing)
            app.screen.post_message(SectionSelected(section_id="vas", index=0))
            await pilot.pause()

            # Make a change to the form
            form = app.screen.query_one(VASConfigForm)
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.changed"
            await pilot.pause()

            # Verify form is dirty
            assert form.is_dirty is True

            # Try to navigate to keyboard
            app.screen.post_message(SectionSelected(section_id="keyboard", index=None))
            await pilot.pause()

            # Dialog should be shown
            assert isinstance(app.screen, UnsavedChangesDialog)

    @pytest.mark.asyncio
    async def test_dialog_save_saves_and_navigates(self) -> None:
        """Clicking Save in dialog should save changes and navigate."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.editor import EditorScreen
        from vtap100.tui.screens.unsaved_changes_dialog import UnsavedChangesDialog
        from vtap100.tui.widgets.forms.keyboard import KeyboardConfigForm
        from vtap100.tui.widgets.forms.vas import VASConfigForm
        from vtap100.tui.widgets.sidebar import SectionSelected

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to VAS and make changes
            app.screen.post_message(SectionSelected(section_id="vas", index=0))
            await pilot.pause()
            form = app.screen.query_one(VASConfigForm)
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.saved"
            await pilot.pause()

            # Try to navigate
            app.screen.post_message(SectionSelected(section_id="keyboard", index=None))
            await pilot.pause()

            # Dialog should be shown
            assert isinstance(app.screen, UnsavedChangesDialog)

            # Click Save
            await pilot.click("#save-btn")
            await pilot.pause()

            # Should be back to editor with keyboard form
            assert isinstance(app.screen, EditorScreen)

            # Changes should be saved
            assert app.config.vas_configs[0].merchant_id == "pass.com.example.saved"

            # Should now show keyboard form
            keyboard_form = app.screen.query_one(KeyboardConfigForm)
            assert keyboard_form is not None

    @pytest.mark.asyncio
    async def test_dialog_discard_discards_and_navigates(self) -> None:
        """Clicking Discard in dialog should discard changes and navigate."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.editor import EditorScreen
        from vtap100.tui.screens.unsaved_changes_dialog import UnsavedChangesDialog
        from vtap100.tui.widgets.forms.keyboard import KeyboardConfigForm
        from vtap100.tui.widgets.forms.vas import VASConfigForm
        from vtap100.tui.widgets.sidebar import SectionSelected

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to VAS and make changes
            app.screen.post_message(SectionSelected(section_id="vas", index=0))
            await pilot.pause()
            form = app.screen.query_one(VASConfigForm)
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.discarded"
            await pilot.pause()

            # Try to navigate
            app.screen.post_message(SectionSelected(section_id="keyboard", index=None))
            await pilot.pause()

            # Dialog should be shown
            assert isinstance(app.screen, UnsavedChangesDialog)

            # Click Discard
            await pilot.click("#discard-btn")
            await pilot.pause()

            # Should be back to editor
            assert isinstance(app.screen, EditorScreen)

            # Changes should NOT be saved (original value remains)
            assert app.config.vas_configs[0].merchant_id == "pass.com.example.test"

            # Should now show keyboard form
            keyboard_form = app.screen.query_one(KeyboardConfigForm)
            assert keyboard_form is not None

    @pytest.mark.asyncio
    async def test_dialog_cancel_stays_on_current_form(self) -> None:
        """Clicking Cancel in dialog should stay on current form."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.editor import EditorScreen
        from vtap100.tui.screens.unsaved_changes_dialog import UnsavedChangesDialog
        from vtap100.tui.widgets.forms.vas import VASConfigForm
        from vtap100.tui.widgets.sidebar import SectionSelected

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to VAS and make changes
            app.screen.post_message(SectionSelected(section_id="vas", index=0))
            await pilot.pause()
            form = app.screen.query_one(VASConfigForm)
            merchant_input = form.query_one("#merchant_id", Input)
            original_changed_value = "pass.com.example.stillchanged"
            merchant_input.value = original_changed_value
            await pilot.pause()

            # Try to navigate
            app.screen.post_message(SectionSelected(section_id="keyboard", index=None))
            await pilot.pause()

            # Dialog should be shown
            assert isinstance(app.screen, UnsavedChangesDialog)

            # Click Cancel
            await pilot.click("#cancel-btn")
            await pilot.pause()

            # Should be back to editor (not navigated away)
            assert isinstance(app.screen, EditorScreen)

            # Should still be on VAS form with unsaved changes
            vas_form = app.screen.query_one(VASConfigForm)
            assert vas_form is not None
            merchant_input = vas_form.query_one("#merchant_id", Input)
            assert merchant_input.value == original_changed_value

            # Changes still not saved
            assert app.config.vas_configs[0].merchant_id == "pass.com.example.test"

    @pytest.mark.asyncio
    async def test_dialog_escape_cancels(self) -> None:
        """Pressing Escape on dialog should cancel (same as Cancel button)."""
        from textual.widgets import Input
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.editor import EditorScreen
        from vtap100.tui.screens.unsaved_changes_dialog import UnsavedChangesDialog
        from vtap100.tui.widgets.forms.vas import VASConfigForm
        from vtap100.tui.widgets.sidebar import SectionSelected

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Navigate to VAS and make changes
            app.screen.post_message(SectionSelected(section_id="vas", index=0))
            await pilot.pause()
            form = app.screen.query_one(VASConfigForm)
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.changed"
            await pilot.pause()

            # Try to navigate
            app.screen.post_message(SectionSelected(section_id="keyboard", index=None))
            await pilot.pause()

            # Dialog should be shown
            assert isinstance(app.screen, UnsavedChangesDialog)

            # Press Escape
            await pilot.press("escape")
            await pilot.pause()

            # Should be back to editor (not navigated away)
            assert isinstance(app.screen, EditorScreen)

            # Should still be on VAS form
            vas_form = app.screen.query_one(VASConfigForm)
            assert vas_form is not None
