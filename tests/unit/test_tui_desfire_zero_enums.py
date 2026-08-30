"""Regression tests for DESFire enum members whose value is zero.

`DESFireCryptoMode.NONE` and `DESFireDataFormat.RAW` are both 0. The form's
Select options mapped their labels to None — the same value used for "not set" —
so a configuration stating `DESFire1Format=0` produced a model value that was
absent from the widget's options, and opening the DESFire section crashed with
InvalidSelectValueError on mount.

Real deployment configurations set `DESFire1Format=0`, so this reproduces with
the files this project exists to support.
"""

from pathlib import Path
import pytest
from textual.widgets import Select
from textual.widgets import Tree
from vtap100.models.config import VTAPConfig
from vtap100.models.desfire import DESFireAppConfig
from vtap100.models.desfire import DESFireConfig
from vtap100.models.desfire import DESFireCryptoMode
from vtap100.models.desfire import DESFireDataFormat


DESFIRE_SECTION_INDEX = 4


async def _open_desfire_section(app, pilot) -> object:
    """Navigate the sidebar to the first DESFire entry and return main content.

    Mounting the form is what triggers the defect, so the test has to actually
    reach the section rather than merely construct the app.
    """
    await pilot.pause()
    sidebar = app.screen.query_one("#sidebar")
    tree = sidebar.query_one(Tree)
    node = tree.root.children[DESFIRE_SECTION_INDEX]
    node.expand()
    await pilot.pause()
    tree.select_node(node.children[0])
    await pilot.pause()
    await pilot.pause()
    return app.screen.query_one("#main-content")


def _config_with(**app_kwargs: object) -> VTAPConfig:
    """Build a VTAPConfig carrying a single DESFire app."""
    app = DESFireAppConfig(app_id="AABBCC", **app_kwargs)  # type: ignore[arg-type]
    return VTAPConfig(desfire=DESFireConfig(apps=[app]))


class TestZeroValuedEnumsOpenInTheEditor:
    """Opening the DESFire section must not reject a zero-valued enum."""

    @pytest.mark.asyncio
    async def test_format_raw_opens(self) -> None:
        """DESFire1Format=0 is RAW and must be selectable."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = _config_with(file_id=0, format=DESFireDataFormat.RAW)

        async with app.run_test() as pilot:
            main_content = await _open_desfire_section(app, pilot)
            assert main_content.query_one("#format", Select).value == DESFireDataFormat.RAW

    @pytest.mark.asyncio
    async def test_crypto_none_opens(self) -> None:
        """DESFire1Crypto=0 is NONE and must be selectable."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = _config_with(file_id=0, crypto=DESFireCryptoMode.NONE)

        async with app.run_test() as pilot:
            main_content = await _open_desfire_section(app, pilot)
            assert main_content.query_one("#crypto", Select).value == DESFireCryptoMode.NONE

    @pytest.mark.asyncio
    async def test_absent_enums_still_open(self) -> None:
        """A config setting neither must still show "not set"."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = _config_with(file_id=0)

        async with app.run_test() as pilot:
            main_content = await _open_desfire_section(app, pilot)
            assert main_content.query_one("#format", Select).value is None
            assert main_content.query_one("#crypto", Select).value is None

    @pytest.mark.asyncio
    async def test_flagship_fixture_opens(self) -> None:
        """The real-world fixture sets Format=0; this is the reported crash."""
        from vtap100.parser import parse
        from vtap100.tui.app import VTAPEditorApp

        fixture = (
            Path(__file__).parent.parent / "fixtures" / "valid_configs" / "full_vas_st_desfire.txt"
        )
        app = VTAPEditorApp()
        app.config = parse(fixture.read_text())

        async with app.run_test() as pilot:
            main_content = await _open_desfire_section(app, pilot)
            assert main_content.query_one("#format", Select).value == DESFireDataFormat.RAW


class TestZeroValuedEnumsAreDistinctFromAbsent:
    """An explicit zero and an absent value must not collapse into one another."""

    def test_format_raw_emits_a_line(self) -> None:
        """An explicit Format=0 keeps its line."""
        config = DESFireAppConfig(app_id="AABBCC", format=DESFireDataFormat.RAW)
        assert "DESFire1Format=0" in config.to_config_lines(1)

    def test_absent_format_emits_no_line(self) -> None:
        """An absent format produces nothing."""
        config = DESFireAppConfig(app_id="AABBCC")
        assert not any("Format" in line for line in config.to_config_lines(1))

    def test_crypto_none_emits_a_line(self) -> None:
        """An explicit Crypto=0 keeps its line."""
        config = DESFireAppConfig(app_id="AABBCC", crypto=DESFireCryptoMode.NONE)
        assert "DESFire1Crypto=0" in config.to_config_lines(1)

    @pytest.mark.asyncio
    async def test_saving_preserves_an_explicit_zero(self) -> None:
        """Reopening and saving must not turn Format=0 into an absent value."""
        from vtap100.tui.app import VTAPEditorApp

        app = VTAPEditorApp()
        app.config = _config_with(file_id=0, format=DESFireDataFormat.RAW)

        async with app.run_test() as pilot:
            main_content = await _open_desfire_section(app, pilot)
            form = main_content.query_one("DESFireConfigForm")
            assert form.get_config().format == DESFireDataFormat.RAW
