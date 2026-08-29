"""Unit tests for TUI Preview Widget - Phase 6.

Tests for:
- ConfigPreview widget creation and rendering
- Live preview updates when config changes
- Preview content generation using ConfigGenerator
"""

import pytest
from vtap100.models.vas import AppleVASConfig


class TestPreviewImports:
    """Test that preview module can be imported."""

    def test_import_preview_widget(self) -> None:
        """ConfigPreview should be importable from widgets."""
        from vtap100.tui.widgets.preview import ConfigPreview

        assert ConfigPreview is not None


class TestConfigPreview:
    """Test ConfigPreview widget."""

    def test_preview_creation(self) -> None:
        """ConfigPreview should be creatable."""
        from vtap100.tui.widgets.preview import ConfigPreview

        preview = ConfigPreview()
        assert preview is not None

    def test_preview_has_update_method(self) -> None:
        """ConfigPreview should have update_preview method."""
        from vtap100.tui.widgets.preview import ConfigPreview

        preview = ConfigPreview()
        assert hasattr(preview, "update_preview")
        assert callable(preview.update_preview)


class TestConfigPreviewAsync:
    """Async tests for ConfigPreview widget."""

    @pytest.mark.asyncio
    async def test_preview_renders_empty_config(self) -> None:
        """Preview should render empty config header."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Get the preview widget
            from vtap100.tui.widgets.preview import ConfigPreview

            preview = app.screen.query_one("#preview-widget", ConfigPreview)
            content = preview.get_preview_content()

            # Should at least have the header
            assert "!VTAPconfig" in content

    @pytest.mark.asyncio
    async def test_preview_shows_vas_config(self) -> None:
        """Preview should show VAS config when added."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Add a VAS config
            vas = AppleVASConfig(slot=1, merchant_id="pass.com.example.test", key_slot=1)
            app.config.vas_configs.append(vas)

            # Get preview and refresh
            from vtap100.tui.widgets.preview import ConfigPreview

            preview = app.screen.query_one("#preview-widget", ConfigPreview)
            preview.update_preview(app.config)

            content = preview.get_preview_content()
            assert "VAS1MerchantID=pass.com.example.test" in content
            assert "VAS1KeySlot=1" in content

    @pytest.mark.asyncio
    async def test_preview_updates_on_config_change(self) -> None:
        """Preview should update when config changes."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            from vtap100.tui.widgets.preview import ConfigPreview

            preview = app.screen.query_one("#preview-widget", ConfigPreview)

            # Initially empty
            content1 = preview.get_preview_content()
            assert "VAS1MerchantID" not in content1

            # Add VAS config and update
            vas = AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=2)
            app.config.vas_configs.append(vas)
            preview.update_preview(app.config)

            # Now should have VAS
            content2 = preview.get_preview_content()
            assert "VAS1MerchantID=pass.com.test" in content2
            assert "VAS1KeySlot=2" in content2

    @pytest.mark.asyncio
    async def test_preview_panel_contains_preview_widget(self) -> None:
        """Preview panel should contain the ConfigPreview widget."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            from vtap100.tui.widgets.preview import ConfigPreview

            # Should be able to query the preview widget inside preview-panel
            preview_panel = app.screen.query_one("#preview-panel")
            preview_widget = preview_panel.query_one(ConfigPreview)
            assert preview_widget is not None


class TestPreviewToggle:
    """Test preview panel 3-state toggle."""

    @pytest.mark.asyncio
    async def test_preview_default_state(self) -> None:
        """Preview should start in default state (visible, normal size)."""
        from vtap100.tui.app import PreviewMode
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Default mode should be DEFAULT
            assert app.preview_mode == PreviewMode.DEFAULT

            # Preview panel should be visible
            preview_panel = app.screen.query_one("#preview-panel")
            assert preview_panel.display is True

            # Top row (sidebar, main, help) should be visible
            top_row = app.screen.query_one("#top-row")
            assert top_row.display is True

    @pytest.mark.asyncio
    async def test_preview_toggle_to_maximized(self) -> None:
        """Ctrl+O should cycle preview from default to maximized."""
        from vtap100.tui.app import PreviewMode
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press Ctrl+O to toggle
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Should now be in maximized mode
            assert app.preview_mode == PreviewMode.MAXIMIZED

            # Preview panel should be visible
            preview_panel = app.screen.query_one("#preview-panel")
            assert preview_panel.display is True

            # Top row should be hidden (maximized preview takes full space)
            top_row = app.screen.query_one("#top-row")
            assert top_row.display is False

    @pytest.mark.asyncio
    async def test_preview_toggle_to_hidden(self) -> None:
        """Ctrl+O twice should cycle preview to hidden."""
        from vtap100.tui.app import PreviewMode
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press Ctrl+O twice: default -> maximized -> hidden
            await pilot.press("ctrl+o")
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Should now be in hidden mode
            assert app.preview_mode == PreviewMode.HIDDEN

            # Preview panel should be hidden
            preview_panel = app.screen.query_one("#preview-panel")
            assert preview_panel.display is False

            # Top row should be visible again
            top_row = app.screen.query_one("#top-row")
            assert top_row.display is True

    @pytest.mark.asyncio
    async def test_preview_toggle_cycle_back_to_default(self) -> None:
        """Ctrl+O three times should cycle back to default."""
        from vtap100.tui.app import PreviewMode
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press Ctrl+O three times: default -> maximized -> hidden -> default
            await pilot.press("ctrl+o")
            await pilot.press("ctrl+o")
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Should be back to default mode
            assert app.preview_mode == PreviewMode.DEFAULT

            # Preview panel should be visible
            preview_panel = app.screen.query_one("#preview-panel")
            assert preview_panel.display is True

            # Top row should be visible
            top_row = app.screen.query_one("#top-row")
            assert top_row.display is True

    @pytest.mark.asyncio
    async def test_preview_maximized_has_full_height(self) -> None:
        """Maximized preview should have full height CSS class."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Toggle to maximized
            await pilot.press("ctrl+o")
            await pilot.pause()

            # Preview panel should have maximized class
            preview_panel = app.screen.query_one("#preview-panel")
            assert "preview-maximized" in preview_panel.classes


class TestConfigPreviewEdgeCases:
    """Test edge cases for ConfigPreview widget."""

    def test_update_preview_before_mount(self) -> None:
        """update_preview should handle widget not being mounted yet."""
        from vtap100.models.config import VTAPConfig
        from vtap100.tui.widgets.preview import ConfigPreview

        # Create preview widget but don't mount it
        preview = ConfigPreview()

        # Update should not raise even though widget is not mounted
        config = VTAPConfig()
        preview.update_preview(config)

        # Content should still be updated internally
        content = preview.get_preview_content()
        assert "!VTAPconfig" in content

    def test_update_preview_exception_handling(self) -> None:
        """update_preview should catch exceptions gracefully."""
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig
        from vtap100.tui.widgets.preview import ConfigPreview

        preview = ConfigPreview()

        # Call update_preview without mounting - should not raise
        config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)]
        )
        preview.update_preview(config)

        # Content should be updated
        content = preview.get_preview_content()
        assert "VAS1MerchantID=pass.com.test" in content

    def test_preview_with_initial_config(self) -> None:
        """ConfigPreview should accept initial config."""
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig
        from vtap100.tui.widgets.preview import ConfigPreview

        config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.initial", key_slot=2)]
        )
        preview = ConfigPreview(config=config)

        # Internal config should be set (content generated on compose)
        assert preview._config == config

    def test_preview_generate_content(self) -> None:
        """_generate_content should use ConfigGenerator."""
        from vtap100.models.config import VTAPConfig
        from vtap100.models.vas import AppleVASConfig
        from vtap100.tui.widgets.preview import ConfigPreview

        config = VTAPConfig(
            vas_configs=[AppleVASConfig(slot=1, merchant_id="pass.com.gen", key_slot=3)]
        )
        preview = ConfigPreview(config=config)

        # Call _generate_content directly
        content = preview._generate_content()
        assert "!VTAPconfig" in content
        assert "VAS1MerchantID=pass.com.gen" in content
        assert "VAS1KeySlot=3" in content
