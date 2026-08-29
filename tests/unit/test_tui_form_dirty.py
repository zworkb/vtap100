"""Unit tests for form dirty state tracking.

TDD Red Phase: These tests define the expected behavior of the
dirty state tracking feature in form widgets.
"""

import pytest
from vtap100.models.config import VTAPConfig
from vtap100.models.keyboard import KeyboardConfig
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.models.vas import AppleVASConfig


class TestFormDirtyStateBasic:
    """Tests for basic dirty state functionality."""

    def test_new_form_is_not_dirty(self) -> None:
        """A newly created form should not be dirty."""
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        config = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        form = VASConfigForm(config=config, index=0, is_new=False)
        assert hasattr(form, "is_dirty")
        assert form.is_dirty is False

    def test_form_has_mark_saved_method(self) -> None:
        """Form should have a mark_saved method."""
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        config = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        form = VASConfigForm(config=config, index=0, is_new=False)
        assert hasattr(form, "mark_saved")
        assert callable(form.mark_saved)

    def test_form_has_get_form_values_method(self) -> None:
        """Form should have a method to get current form values."""
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        config = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
        form = VASConfigForm(config=config, index=0, is_new=False)
        assert hasattr(form, "get_form_values")
        assert callable(form.get_form_values)


class TestFormDirtyStateAsync:
    """Async tests for dirty state with mounted forms."""

    @pytest.mark.asyncio
    async def test_form_becomes_dirty_on_input_change(self) -> None:
        """Form should become dirty when input value changes."""
        from textual.app import App
        from textual.widgets import Input
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        class TestApp(App[None]):
            config = VTAPConfig()

            def compose(self):
                vas_config = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
                yield VASConfigForm(config=vas_config, index=0, is_new=False)

        async with TestApp().run_test() as pilot:
            await pilot.pause()
            form = pilot.app.query_one(VASConfigForm)

            # Initially not dirty
            assert form.is_dirty is False

            # Type into the merchant_id field to change it
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.changed"
            await pilot.pause()

            # Now should be dirty
            assert form.is_dirty is True

    @pytest.mark.asyncio
    async def test_form_dirty_after_switch_change(self) -> None:
        """Form should become dirty when a switch is toggled."""
        from textual.app import App
        from textual.widgets import Switch
        from vtap100.tui.widgets.forms.keyboard import KeyboardConfigForm

        class TestApp(App[None]):
            def compose(self):
                config = KeyboardConfig(log_mode=False)
                yield KeyboardConfigForm(config=config)

        async with TestApp().run_test() as pilot:
            await pilot.pause()
            form = pilot.app.query_one(KeyboardConfigForm)

            # Initially not dirty
            assert form.is_dirty is False

            # Toggle the log_mode switch
            switch = form.query_one("#log_mode", Switch)
            switch.value = True
            await pilot.pause()

            # Now should be dirty
            assert form.is_dirty is True

    @pytest.mark.asyncio
    async def test_mark_saved_clears_dirty_state(self) -> None:
        """Calling mark_saved should clear the dirty state."""
        from textual.app import App
        from textual.widgets import Input
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        class TestApp(App[None]):
            config = VTAPConfig()

            def compose(self):
                vas_config = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
                yield VASConfigForm(config=vas_config, index=0, is_new=False)

        async with TestApp().run_test() as pilot:
            await pilot.pause()
            form = pilot.app.query_one(VASConfigForm)

            # Make form dirty
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.changed"
            await pilot.pause()
            assert form.is_dirty is True

            # Mark as saved
            form.mark_saved()

            # Should no longer be dirty
            assert form.is_dirty is False

    @pytest.mark.asyncio
    async def test_reverting_to_original_value_makes_form_clean(self) -> None:
        """Reverting a field to its original value should make the form clean."""
        from textual.app import App
        from textual.widgets import Input
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        class TestApp(App[None]):
            config = VTAPConfig()

            def compose(self):
                vas_config = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
                yield VASConfigForm(config=vas_config, index=0, is_new=False)

        async with TestApp().run_test() as pilot:
            await pilot.pause()
            form = pilot.app.query_one(VASConfigForm)
            merchant_input = form.query_one("#merchant_id", Input)

            original_value = merchant_input.value

            # Change the value
            merchant_input.value = "pass.com.example.changed"
            await pilot.pause()
            assert form.is_dirty is True

            # Revert to original
            merchant_input.value = original_value
            await pilot.pause()

            # Should be clean again
            assert form.is_dirty is False


class TestFormDirtyStateSmartTap:
    """Tests for dirty state on SmartTap forms."""

    @pytest.mark.asyncio
    async def test_smarttap_form_dirty_tracking(self) -> None:
        """SmartTap form should also support dirty tracking."""
        from textual.app import App
        from textual.widgets import Input
        from vtap100.tui.widgets.forms.smarttap import SmartTapConfigForm

        class TestApp(App[None]):
            config = VTAPConfig()

            def compose(self):
                st_config = GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=1)
                yield SmartTapConfigForm(config=st_config, index=0, is_new=False)

        async with TestApp().run_test() as pilot:
            await pilot.pause()
            form = pilot.app.query_one(SmartTapConfigForm)

            # Initially not dirty
            assert form.is_dirty is False

            # Change collector_id
            collector_input = form.query_one("#collector_id", Input)
            collector_input.value = "87654321"
            await pilot.pause()

            # Now should be dirty
            assert form.is_dirty is True


class TestNewFormDirtyState:
    """Tests for dirty state on new forms (is_new=True)."""

    @pytest.mark.asyncio
    async def test_new_form_starts_clean(self) -> None:
        """A new form (is_new=True) should NOT be dirty if nothing was changed.

        New empty forms don't have meaningful data to save, so we don't
        warn when navigating away. Forms only become dirty when user
        actually modifies a field.
        """
        from textual.app import App
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        class TestApp(App[None]):
            config = VTAPConfig()

            def compose(self):
                # New form without existing config
                yield VASConfigForm(config=None, index=0, is_new=True)

        async with TestApp().run_test() as pilot:
            await pilot.pause()
            form = pilot.app.query_one(VASConfigForm)

            # New forms without modifications should be clean
            assert form.is_dirty is False

    @pytest.mark.asyncio
    async def test_new_form_becomes_dirty_on_change(self) -> None:
        """A new form should become dirty when user modifies a field."""
        from textual.app import App
        from textual.widgets import Input
        from vtap100.tui.widgets.forms.vas import VASConfigForm

        class TestApp(App[None]):
            config = VTAPConfig()

            def compose(self):
                # New form without existing config
                yield VASConfigForm(config=None, index=0, is_new=True)

        async with TestApp().run_test() as pilot:
            await pilot.pause()
            form = pilot.app.query_one(VASConfigForm)

            # Initially clean
            assert form.is_dirty is False

            # Make a change
            merchant_input = form.query_one("#merchant_id", Input)
            merchant_input.value = "pass.com.example.new"
            await pilot.pause()

            # Now should be dirty
            assert form.is_dirty is True
