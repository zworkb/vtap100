"""Unit tests for TUI Save Function - Phase 6.

Tests for:
- Saving config to file with ConfigGenerator
- Handling missing output path
- Save notification messages
"""

import pytest
from vtap100.models.vas import AppleVASConfig


class TestSaveFunction:
    """Test app save functionality."""

    @pytest.mark.asyncio
    async def test_save_with_output_path(self, tmp_path) -> None:
        """Save should write config to output file."""
        from vtap100.tui.app import VTAPEditorApp

        output_file = tmp_path / "test_output.txt"
        app = VTAPEditorApp(output_path=output_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Add a VAS config
            vas = AppleVASConfig(slot=1, merchant_id="pass.com.example.save", key_slot=1)
            app.config.vas_configs.append(vas)

            # Press Ctrl+S to save
            await pilot.press("ctrl+s")

            # File should exist and contain the config
            assert output_file.exists()
            content = output_file.read_text()
            assert "!VTAPconfig" in content
            assert "VAS1MerchantID=pass.com.example.save" in content

    @pytest.mark.asyncio
    async def test_save_without_output_path_shows_dialog(self) -> None:
        """Save without output path should show save dialog."""
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.save_dialog import SaveDialog

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            # Press Ctrl+S to save (no output path set)
            await pilot.press("ctrl+s")
            await pilot.pause()

            # SaveDialog should be shown
            assert isinstance(app.screen, SaveDialog)

            # Dialog should have default filename "config.txt"
            from textual.widgets import Input

            filename_input = app.screen.query_one("#filename-input", Input)
            assert filename_input.value == "config.txt"

            # Press Escape to cancel
            await pilot.press("escape")
            await pilot.pause()

            # Should be back to main screen
            assert not isinstance(app.screen, SaveDialog)

    @pytest.mark.asyncio
    async def test_save_dialog_saves_file(self, tmp_path) -> None:
        """Save dialog should save file when confirmed."""
        import os
        from vtap100.models.vas import AppleVASConfig
        from vtap100.tui.app import VTAPEditorApp
        from vtap100.tui.screens.save_dialog import SaveDialog

        # Change to tmp_path so relative filename works
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            app = VTAPEditorApp()

            async with app.run_test() as pilot:
                await pilot.pause()

                # Add a VAS config
                vas = AppleVASConfig(slot=1, merchant_id="pass.com.dialog.test", key_slot=1)
                app.config.vas_configs.append(vas)

                # Press Ctrl+S to save (no output path set)
                await pilot.press("ctrl+s")
                await pilot.pause()

                # SaveDialog should be shown
                assert isinstance(app.screen, SaveDialog)

                # Clear input and type new filename
                from textual.widgets import Input

                filename_input = app.screen.query_one("#filename-input", Input)
                filename_input.value = "my_config.txt"

                # Click save button
                await pilot.click("#save-btn")
                await pilot.pause()

                # File should exist
                output_file = tmp_path / "my_config.txt"
                assert output_file.exists()
                content = output_file.read_text()
                assert "VAS1MerchantID=pass.com.dialog.test" in content

                # output_path should be set for future saves
                assert app.output_path is not None
        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_save_empty_config(self, tmp_path) -> None:
        """Save should work with empty config."""
        from vtap100.tui.app import VTAPEditorApp

        output_file = tmp_path / "empty_config.txt"
        app = VTAPEditorApp(output_path=output_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Press Ctrl+S to save
            await pilot.press("ctrl+s")

            # File should exist with at least the header
            assert output_file.exists()
            content = output_file.read_text()
            assert "!VTAPconfig" in content

    @pytest.mark.asyncio
    async def test_save_overwrites_existing_file(self, tmp_path) -> None:
        """Save should overwrite existing file."""
        from vtap100.tui.app import VTAPEditorApp

        output_file = tmp_path / "overwrite_test.txt"
        output_file.write_text("old content")

        app = VTAPEditorApp(output_path=output_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Add a VAS config
            vas = AppleVASConfig(slot=1, merchant_id="pass.com.new", key_slot=2)
            app.config.vas_configs.append(vas)

            # Press Ctrl+S to save
            await pilot.press("ctrl+s")

            # Old content should be replaced
            content = output_file.read_text()
            assert "old content" not in content
            assert "!VTAPconfig" in content
            assert "VAS1MerchantID=pass.com.new" in content

    @pytest.mark.asyncio
    async def test_save_multiple_configs(self, tmp_path) -> None:
        """Save should include all configured sections."""
        from vtap100.models.smarttap import GoogleSmartTapConfig
        from vtap100.tui.app import VTAPEditorApp

        output_file = tmp_path / "multi_config.txt"
        app = VTAPEditorApp(output_path=output_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Add VAS and SmartTap configs
            vas = AppleVASConfig(slot=1, merchant_id="pass.com.test", key_slot=1)
            st = GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=2)
            app.config.vas_configs.append(vas)
            app.config.smarttap_configs.append(st)

            # Press Ctrl+S to save
            await pilot.press("ctrl+s")

            # File should contain both configs
            content = output_file.read_text()
            assert "VAS1MerchantID=pass.com.test" in content
            # ST1 does not work, generator starts at ST2
            assert "ST2CollectorID=12345678" in content
