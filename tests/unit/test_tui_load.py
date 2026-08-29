"""Unit tests for TUI Load Function.

Tests for:
- Loading config from file with ConfigParser
- Handling missing input file
- Handling invalid config file
"""

import pytest
from vtap100.models.smarttap import GoogleSmartTapConfig
from vtap100.models.vas import AppleVASConfig


class TestLoadFunction:
    """Test app load functionality."""

    @pytest.mark.asyncio
    async def test_load_with_input_path(self, tmp_path) -> None:
        """Load should read config from input file."""
        from vtap100.tui.app import VTAPEditorApp

        input_file = tmp_path / "test_config.txt"
        input_file.write_text("""!VTAPconfig
VAS1MerchantID=pass.com.example.load
VAS1KeySlot=1
""")

        app = VTAPEditorApp(input_path=input_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Config should be loaded from file
            assert len(app.config.vas_configs) == 1
            assert app.config.vas_configs[0].merchant_id == "pass.com.example.load"
            assert app.config.vas_configs[0].key_slot == 1

    @pytest.mark.asyncio
    async def test_load_without_input_path(self) -> None:
        """Load without input path should create empty config."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()

        async with app.run_test() as pilot:
            await pilot.pause()

            # Config should be empty
            assert len(app.config.vas_configs) == 0
            assert len(app.config.smarttap_configs) == 0
            assert app.config.keyboard is None

    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self, tmp_path) -> None:
        """Load with nonexistent file should create empty config."""
        from vtap100.tui.app import VTAPEditorApp

        input_file = tmp_path / "nonexistent.txt"
        app = VTAPEditorApp(input_path=input_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Config should be empty
            assert len(app.config.vas_configs) == 0

    @pytest.mark.asyncio
    async def test_load_combined_config(self, tmp_path) -> None:
        """Load should parse combined VAS, SmartTap, and Keyboard config."""
        from vtap100.tui.app import VTAPEditorApp

        input_file = tmp_path / "combined_config.txt"
        input_file.write_text("""!VTAPconfig
; Apple VAS Configuration
VAS1MerchantID=pass.com.example.test
VAS1KeySlot=1
; Google Smart Tap Configuration
ST1CollectorID=96972794
ST1KeySlot=2
ST1KeyVersion=1
; Keyboard Emulation
KBLogMode=1
KBSource=AG
""")

        app = VTAPEditorApp(input_path=input_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # VAS should be loaded
            assert len(app.config.vas_configs) == 1
            assert app.config.vas_configs[0].merchant_id == "pass.com.example.test"

            # SmartTap should be loaded
            assert len(app.config.smarttap_configs) == 1
            assert app.config.smarttap_configs[0].collector_id == "96972794"
            assert app.config.smarttap_configs[0].key_slot == 2

            # Keyboard should be loaded
            assert app.config.keyboard is not None
            assert app.config.keyboard.log_mode is True
            assert app.config.keyboard.source == "AG"

    @pytest.mark.asyncio
    async def test_load_sets_output_to_input(self, tmp_path) -> None:
        """Output path should default to input path if not specified."""
        from vtap100.tui.app import VTAPEditorApp

        input_file = tmp_path / "config.txt"
        input_file.write_text("!VTAPconfig\n")

        app = VTAPEditorApp(input_path=input_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Output path should be same as input
            assert app.output_path == input_file

    @pytest.mark.asyncio
    async def test_load_separate_output_path(self, tmp_path) -> None:
        """Output path can be different from input path."""
        from vtap100.tui.app import VTAPEditorApp

        input_file = tmp_path / "input.txt"
        output_file = tmp_path / "output.txt"
        input_file.write_text("!VTAPconfig\n")

        app = VTAPEditorApp(input_path=input_file, output_path=output_file)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Output path should be the specified one
            assert app.output_path == output_file

    @pytest.mark.asyncio
    async def test_roundtrip_save_load(self, tmp_path) -> None:
        """Config should be identical after save and reload."""
        from vtap100.tui.app import VTAPEditorApp

        config_file = tmp_path / "roundtrip.txt"

        # First, create and save a config
        app1 = VTAPEditorApp(output_path=config_file)

        async with app1.run_test() as pilot:
            await pilot.pause()

            # Add configurations
            vas = AppleVASConfig(slot=1, merchant_id="pass.com.roundtrip", key_slot=3)
            st = GoogleSmartTapConfig(slot=2, collector_id="12345678", key_slot=4, key_version=2)
            app1.config.vas_configs.append(vas)
            app1.config.smarttap_configs.append(st)

            # Save
            await pilot.press("ctrl+s")

        # Now reload in a new app instance
        app2 = VTAPEditorApp(input_path=config_file)

        async with app2.run_test() as pilot:
            await pilot.pause()

            # Verify the configs match
            assert len(app2.config.vas_configs) == 1
            assert app2.config.vas_configs[0].merchant_id == "pass.com.roundtrip"
            assert app2.config.vas_configs[0].key_slot == 3

            assert len(app2.config.smarttap_configs) == 1
            assert app2.config.smarttap_configs[0].collector_id == "12345678"
            assert app2.config.smarttap_configs[0].key_slot == 4
