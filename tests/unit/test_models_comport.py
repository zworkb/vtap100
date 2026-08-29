"""Unit tests for serial port configuration."""


class TestComPortConfig:
    """ComPortSource uses the same bitmask as KBSource."""

    def test_config_lines(self) -> None:
        """Only the fields that are set produce lines."""
        from vtap100.models.comport import ComPortConfig

        config = ComPortConfig(enable=False, mode=1, source="A1")
        assert config.to_config_lines() == [
            "ComPortEnable=0",
            "ComPortMode=1",
            "ComPortSource=A1",
        ]

    def test_empty_config_produces_no_lines(self) -> None:
        """A serial config with nothing set emits nothing."""
        from vtap100.models.comport import ComPortConfig

        assert ComPortConfig().to_config_lines() == []

    def test_source_accepts_kbsource_builder_output(self) -> None:
        """The bitmask is shared, so the builder applies unchanged."""
        from vtap100.models.comport import ComPortConfig
        from vtap100.models.keyboard import KBSourceBuilder

        source = KBSourceBuilder().mobile_pass().card_tag_uid().build()
        assert ComPortConfig(source=source).source == "81"

    def test_roundtrip(self) -> None:
        """Serial settings survive a cycle."""
        from vtap100.roundtrip import compare

        text = "!VTAPconfig\nComPortEnable=0\nComPortMode=1\nComPortSource=A1\n"
        assert compare(text).is_lossless
