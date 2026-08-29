"""Unit tests for TUI Sidebar - Phase 2: Navigation.

Tests for:
- ConfigSidebar creation and structure
- Section tree with all config areas
- Badges showing item counts
- Section selection events
"""

import pytest
from vtap100.models.config import VTAPConfig
from vtap100.models.vas import AppleVASConfig


class TestSidebarImports:
    """Test that Sidebar module can be imported."""

    def test_import_config_sidebar(self) -> None:
        """ConfigSidebar should be importable."""
        from vtap100.tui.widgets.sidebar import ConfigSidebar

        assert ConfigSidebar is not None


class TestConfigSidebar:
    """Test ConfigSidebar widget."""

    def test_sidebar_has_sections_property(self) -> None:
        """Sidebar should define sections property with all config areas."""
        from vtap100.tui.widgets.sidebar import ConfigSidebar

        sidebar = ConfigSidebar()
        section_ids = [s[0] for s in sidebar.sections]

        # All config areas should be present
        assert "vas" in section_ids
        assert "smarttap" in section_ids
        assert "keyboard" in section_ids
        assert "nfc" in section_ids
        assert "desfire" in section_ids
        assert "feedback" in section_ids

    def test_sidebar_sections_have_labels(self) -> None:
        """Each section should have id, label, and attribute name."""
        from vtap100.tui.widgets.sidebar import ConfigSidebar

        sidebar = ConfigSidebar()
        for section in sidebar.sections:
            assert len(section) == 3
            section_id, label, attr = section
            assert isinstance(section_id, str)
            assert isinstance(label, str)
            assert isinstance(attr, str)


class TestConfigSidebarAsync:
    """Async tests for ConfigSidebar widget."""

    @pytest.mark.asyncio
    async def test_sidebar_renders_tree(self) -> None:
        """Sidebar should render a tree with sections."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Sidebar should contain a Tree widget
            sidebar = app.screen.query_one("#sidebar")
            trees = sidebar.query(Tree)
            assert len(trees) == 1

    @pytest.mark.asyncio
    async def test_sidebar_tree_has_all_sections(self) -> None:
        """Tree should have nodes for all config sections."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.widgets.sidebar import ConfigSidebar

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#config-sidebar", ConfigSidebar)
            tree = sidebar.query_one(Tree)

            # Root should have children for each section
            root = tree.root
            assert len(root.children) == len(sidebar.sections)

    @pytest.mark.asyncio
    async def test_sidebar_shows_vas_badge_when_configured(self) -> None:
        """Sidebar should show badge with count when VAS is configured."""
        from textual.widgets import Tree
        from vtap100.tui.app import VTAPEditorApp

        # Create app with VAS config
        app = VTAPEditorApp()
        app.config = VTAPConfig(
            vas_configs=[
                AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1),
            ]
        )

        async with app.run_test() as pilot:
            await pilot.pause()

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)

            # Find VAS node and check it has a badge
            vas_node = None
            for child in tree.root.children:
                if child.data == "vas":
                    vas_node = child
                    break

            assert vas_node is not None
            # Label should contain badge like "[1]"
            assert "[1]" in str(vas_node.label)


class TestSidebarSelection:
    """Test sidebar section selection."""

    @pytest.mark.asyncio
    async def test_selecting_neuer_eintrag_posts_message(self) -> None:
        """Selecting 'Neuer Eintrag' should post a SectionSelected message."""
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.widgets.sidebar import SectionSelected

        app = VTAPEditorApp()
        messages_received: list[SectionSelected] = []

        # Monkey-patch to capture messages
        original_post = app.post_message

        def capture_post(msg):
            if isinstance(msg, SectionSelected):
                messages_received.append(msg)
            return original_post(msg)

        app.post_message = capture_post

        async with app.run_test() as pilot:
            await pilot.pause()

            # Click on a tree node (simulate selection)
            from textual.widgets import Tree

            sidebar = app.screen.query_one("#sidebar")
            tree = sidebar.query_one(Tree)

            # Select "Neuer Eintrag" under VAS
            vas_node = tree.root.children[0]
            neuer_eintrag = vas_node.children[0]
            tree.select_node(neuer_eintrag)
            await pilot.pause()

            # Should have received a SectionSelected message
            assert len(messages_received) >= 1
            assert messages_received[0].section_id == "vas"
            assert messages_received[0].index is None  # New entry has no index
