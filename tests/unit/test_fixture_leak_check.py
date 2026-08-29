"""Unit tests for the fixture leak check.

The check is an allowlist: fixtures may only contain placeholder identifiers.
"""

from pathlib import Path


class TestCheckFile:
    """Violations that must be caught before a commit reaches a public repo."""

    def test_clean_fixture_passes(self, tmp_path: Path) -> None:
        """A fixture using only placeholders is accepted."""
        from check_fixture_leaks import check_file

        f = tmp_path / "clean.txt"
        f.write_text(
            "!VTAPconfig\n"
            "VAS2MerchantID=pass.com.example.library-card\n"
            "ST2CollectorID=12345678\n"
            "DESFire1AppID=AABBCC\n"
            "AccessTCI=020000\n"
        )
        assert check_file(f) == []

    def test_key_material_is_rejected(self, tmp_path: Path) -> None:
        """A PEM block must never be committed, whatever the file is called."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("-----BEGIN EC PRIVATE KEY-----\nMHcCAQ\n")
        assert any("key material" in m for m in check_file(f))

    def test_real_merchant_id_is_rejected(self, tmp_path: Path) -> None:
        """Merchant IDs must sit under pass.com.example."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("!VTAPconfig\nVAS2MerchantID=pass.de.somewhere.library-card\n")
        assert any("MerchantID" in m for m in check_file(f))

    def test_unlisted_collector_id_is_rejected(self, tmp_path: Path) -> None:
        """Collector IDs must come from the placeholder set."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("!VTAPconfig\nST2CollectorID=99887766\n")
        assert any("CollectorID" in m for m in check_file(f))

    def test_unlisted_app_id_is_rejected(self, tmp_path: Path) -> None:
        """DESFire AIDs must come from the placeholder set."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("!VTAPconfig\nDESFire1AppID=D0FFEE\n")
        assert any("AppID" in m for m in check_file(f))

    def test_long_hex_in_comment_is_rejected(self, tmp_path: Path) -> None:
        """A System Identifier blob in a comment is still an identifier."""
        from check_fixture_leaks import check_file

        f = tmp_path / "leak.txt"
        f.write_text("; SysID: 4E4F545F415F5245414C5F5359534944 (16B)\n")
        assert any("hex" in m for m in check_file(f))

    def test_placeholder_sysid_in_comment_passes(self, tmp_path: Path) -> None:
        """The placeholder System Identifier is allowed."""
        from check_fixture_leaks import check_file

        f = tmp_path / "clean.txt"
        f.write_text("; SysID: 4558414D504C455F7379735F31303030 (16B)\n")
        assert check_file(f) == []


class TestMain:
    """Exit code contract for pre-commit."""

    def test_returns_one_when_a_file_leaks(self, tmp_path: Path) -> None:
        """A violation fails the commit."""
        from check_fixture_leaks import main

        f = tmp_path / "leak.txt"
        f.write_text("-----BEGIN EC PRIVATE KEY-----\n")
        assert main([str(f)]) == 1

    def test_returns_zero_when_clean(self, tmp_path: Path) -> None:
        """No violation, no obstruction."""
        from check_fixture_leaks import main

        f = tmp_path / "clean.txt"
        f.write_text("!VTAPconfig\nVAS1MerchantID=pass.com.example.x\n")
        assert main([str(f)]) == 0
