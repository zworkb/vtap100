"""Unit tests for the round-trip comparison module."""


class TestExtractSettings:
    """Tests for extracting Key=Value pairs from config text."""

    def test_extracts_key_value_pairs(self) -> None:
        """Plain settings become a dict."""
        from vtap100.roundtrip import extract_settings

        result = extract_settings("!VTAPconfig\nVAS1KeySlot=2\nKBSource=81\n")
        assert result == {"VAS1KeySlot": "2", "KBSource": "81"}

    def test_ignores_comments_and_blank_lines(self) -> None:
        """Comment lines and blanks are not settings."""
        from vtap100.roundtrip import extract_settings

        text = "!VTAPconfig\n\n; a comment\n;KBPassStart=0\nKBSource=81\n"
        assert extract_settings(text) == {"KBSource": "81"}

    def test_keeps_value_containing_equals(self) -> None:
        """Only the first '=' separates key from value."""
        from vtap100.roundtrip import extract_settings

        result = extract_settings("VAS1MerchantURL=https://x.example/?a=b\n")
        assert result == {"VAS1MerchantURL": "https://x.example/?a=b"}


class TestNormalisation:
    """Tests for documented-alias normalisation."""

    def test_nfctype_numeric_alias_equals_letter(self) -> None:
        """NFCType4=1 and NFCType4=U are the same setting."""
        from vtap100.roundtrip import normalise

        assert normalise("NFCType4", "1") == normalise("NFCType4", "U")

    def test_unrelated_setting_is_compared_verbatim(self) -> None:
        """Normalisation applies only to documented aliases."""
        from vtap100.roundtrip import normalise

        assert normalise("KBSource", "81") == "81"
        assert normalise("KBSource", "1") != normalise("KBSource", "U")


class TestCompare:
    """Tests for the round-trip report."""

    def test_lossless_config_reports_no_loss(self) -> None:
        """A config the tool fully supports round-trips cleanly."""
        from vtap100.roundtrip import compare

        report = compare("!VTAPconfig\nVAS1MerchantID=pass.com.example.x\nVAS1KeySlot=1\n")
        assert report.is_lossless
        assert report.lost == []
        assert report.changed == []

    def test_reports_lost_setting(self) -> None:
        """A setting the tool does not support is reported as lost.

        BTEnable is a Bluetooth setting and an explicit non-goal (spec section
        4), so it stays unsupported and this test stays valid. Do not use a
        setting that a later task adds support for.
        """
        from vtap100.roundtrip import compare

        report = compare(
            "!VTAPconfig\nVAS1MerchantID=pass.com.example.x\nVAS1KeySlot=1\nBTEnable=1\n"
        )
        assert "BTEnable" in report.lost
        assert not report.is_lossless
