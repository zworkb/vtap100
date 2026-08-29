"""Unit tests for TUI Help System - Phase 4.

Tests for:
- HelpLoader class
- HelpPanel widget
- Context-sensitive help updates
"""

import pytest
from vtap100.models.config import VTAPConfig
from vtap100.models.vas import AppleVASConfig


class TestHelpLoaderImports:
    """Test that help system modules can be imported."""

    def test_import_help_loader(self) -> None:
        """HelpLoader should be importable."""
        from vtap100.tui.help import HelpLoader

        assert HelpLoader is not None

    def test_import_help_panel(self) -> None:
        """HelpPanel should be importable."""
        from vtap100.tui.widgets.help_panel import HelpPanel

        assert HelpPanel is not None


class TestHelpLoader:
    """Test HelpLoader class."""

    def test_load_all_returns_dict(self) -> None:
        """HelpLoader.load_all() should return a dictionary."""
        from vtap100.tui.help import HelpLoader

        result = HelpLoader.load_all()
        assert isinstance(result, dict)

    def test_load_all_contains_vas_section(self) -> None:
        """HelpLoader should load VAS section help."""
        from vtap100.tui.help import HelpLoader

        result = HelpLoader.load_all()
        assert "vas" in result

    def test_load_all_contains_vas_fields(self) -> None:
        """HelpLoader should load VAS field help."""
        from vtap100.tui.help import HelpLoader

        result = HelpLoader.load_all()
        # Should have "vas.merchant_id", "vas.key_slot" etc.
        assert "vas.merchant_id" in result

    def test_vas_merchant_id_has_title(self) -> None:
        """VAS merchant_id help should have a title."""
        from vtap100.tui.help import HelpLoader

        result = HelpLoader.load_all()
        merchant_id_help = result.get("vas.merchant_id", {})
        assert "title" in merchant_id_help

    def test_vas_merchant_id_has_description(self) -> None:
        """VAS merchant_id help should have a description."""
        from vtap100.tui.help import HelpLoader

        result = HelpLoader.load_all()
        merchant_id_help = result.get("vas.merchant_id", {})
        assert "description" in merchant_id_help

    def test_load_all_contains_smarttap_section(self) -> None:
        """HelpLoader should load SmartTap section help."""
        from vtap100.tui.help import HelpLoader

        result = HelpLoader.load_all()
        assert "smarttap" in result

    def test_load_all_contains_smarttap_fields(self) -> None:
        """HelpLoader should load SmartTap field help."""
        from vtap100.tui.help import HelpLoader

        result = HelpLoader.load_all()
        assert "smarttap.collector_id" in result

    def test_help_loader_is_cached(self) -> None:
        """HelpLoader.load_all() should be cached (same instance returned)."""
        from vtap100.tui.help import HelpLoader

        result1 = HelpLoader.load_all()
        result2 = HelpLoader.load_all()
        # Should be same object due to lru_cache
        assert result1 is result2


class TestHelpPanel:
    """Test HelpPanel widget."""

    def test_help_panel_has_current_context(self) -> None:
        """HelpPanel should have current_context reactive attribute."""
        from vtap100.tui.widgets.help_panel import HelpPanel

        panel = HelpPanel()
        assert hasattr(panel, "current_context")

    def test_help_panel_initial_context_is_empty(self) -> None:
        """HelpPanel should start with empty context."""
        from vtap100.tui.widgets.help_panel import HelpPanel

        panel = HelpPanel()
        assert panel.current_context == ""


class TestHelpPanelAsync:
    """Async tests for HelpPanel widget."""

    @pytest.mark.asyncio
    async def test_help_panel_renders_content(self) -> None:
        """HelpPanel should render help content."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            # HelpPanel should exist in the layout
            help_panel = app.screen.query_one("#help-panel")
            assert help_panel is not None

    @pytest.mark.asyncio
    async def test_help_panel_updates_on_focus(self) -> None:
        """HelpPanel should update when input field gets focus."""
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.widgets.help_panel import HelpPanel

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select VAS entry to show form
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            # Wait for async form loading
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            # Get help panel (widget id is help-panel-widget, container is help-panel)
            help_panel = app.screen.query_one("#help-panel-widget", HelpPanel)

            # Focus merchant_id input - the form should be loaded now
            merchant_input = app.screen.query_one("#merchant_id", Input)
            merchant_input.focus()
            await pilot.pause()

            # Help panel context should update
            assert help_panel.current_context == "vas.merchant_id"

    @pytest.mark.asyncio
    async def test_help_panel_shows_relevant_content(self) -> None:
        """HelpPanel should show content relevant to focused field."""
        from textual.widgets import Input
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.widgets.help_panel import HelpPanel

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select VAS entry to show form
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            # Wait for async form loading
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            # Get help panel (widget id is help-panel-widget, container is help-panel)
            help_panel = app.screen.query_one("#help-panel-widget", HelpPanel)

            # Focus merchant_id input - the form should be loaded now
            merchant_input = app.screen.query_one("#merchant_id", Input)
            merchant_input.focus()
            await pilot.pause()

            # Render help panel and check content contains relevant text
            rendered = str(help_panel.render())
            assert "Merchant" in rendered or "pass." in rendered

    @pytest.mark.asyncio
    async def test_help_panel_updates_on_select_focus(self) -> None:
        """HelpPanel should update when Select field gets focus."""
        from textual.widgets import Select
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.widgets.help_panel import HelpPanel

        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            # Select VAS entry to show form
            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)
            vas_node = tree.root.children[0]
            tree.select_node(vas_node.children[0])
            # Wait for async form loading
            await pilot.pause()
            await pilot.pause()
            await pilot.pause()

            # Get help panel
            help_panel = app.screen.query_one("#help-panel-widget", HelpPanel)

            # Focus key_slot Select
            key_slot_select = app.screen.query_one("#key_slot", Select)
            key_slot_select.focus()
            await pilot.pause()

            # Help panel context should update to key_slot
            assert help_panel.current_context == "vas.key_slot"
