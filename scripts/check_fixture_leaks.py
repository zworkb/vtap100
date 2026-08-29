"""Reject real deployment identifiers in committed test fixtures.

This repository is public and its subject matter is key slots and wallet
credentials. A deployment identifier committed by accident stays in the history
even after the file is corrected, so the check runs as a pre-commit hook rather
than as a step someone has to remember.

The rules are an allowlist. A deny list would have to name the real identifiers
it keeps out, publishing them in this file; an allowlist names only the
placeholders, so introducing a new example value is a deliberate edit.
"""

from pathlib import Path
import re
import sys


ALLOWED_MERCHANT_LABEL = "example"
# Values the manufacturer itself publishes at
# https://www.vtapnfc.com/downloads/config.txt. Listing them here discloses
# nothing that is not already public, and vendor_sample.txt is kept verbatim.
ALLOWED_VENDOR_MERCHANT_IDS = {"pass.com.pronto.originpass.demo"}
ALLOWED_COLLECTOR_IDS = {"12345678", "87654321", "80644855"}
ALLOWED_APP_IDS = {"AABBCC"}
ALLOWED_TCIS = {"020000", "030000", "02AB40"}
# EXAMPLE_sys_1000 in hex — the placeholder System Identifier.
ALLOWED_HEX_BLOBS = {"4558414D504C455F7379735F31303030"}

MERCHANT_ID = re.compile(r"^VAS\d*MerchantID=(.+)$")
COLLECTOR_ID = re.compile(r"^ST\d*CollectorID=(.+)$")
APP_ID = re.compile(r"^DESFire\d*AppID=(.+)$")
ACCESS_TCI = re.compile(r"^AccessTCI=(.+)$")
LONG_HEX = re.compile(r"[0-9A-Fa-f]{24,}")


def check_file(path: Path) -> list[str]:
    """Check one file for identifiers that must not reach a public repository.

    Args:
        path: File to inspect.

    Returns:
        One message per violation; empty when the file is clean.
    """
    problems: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return problems

    allowed_blobs = {blob.upper() for blob in ALLOWED_HEX_BLOBS}

    for number, line in enumerate(text.splitlines(), start=1):
        where = f"{path}:{number}"

        if "-----BEGIN" in line:
            problems.append(f"{where}: key material must never be committed")
            continue

        stripped = line.strip()

        if match := MERCHANT_ID.match(stripped):
            # Membership of the example domain, not a fixed prefix: fixtures for
            # rejection cases carry deliberately malformed IDs such as
            # "com.example.missing-pass-prefix", which leak nothing.
            merchant_id = match.group(1)
            if (
                ALLOWED_MERCHANT_LABEL not in merchant_id.split(".")
                and merchant_id not in ALLOWED_VENDOR_MERCHANT_IDS
            ):
                problems.append(
                    f"{where}: MerchantID must contain the label "
                    f"{ALLOWED_MERCHANT_LABEL!r} (example domain only)"
                )
        elif match := COLLECTOR_ID.match(stripped):
            if match.group(1) not in ALLOWED_COLLECTOR_IDS:
                problems.append(f"{where}: CollectorID is not a known placeholder")
        elif match := APP_ID.match(stripped):
            if match.group(1).upper() not in ALLOWED_APP_IDS:
                problems.append(f"{where}: DESFire AppID is not a known placeholder")
        elif match := ACCESS_TCI.match(stripped):
            if match.group(1).upper() not in ALLOWED_TCIS:
                problems.append(f"{where}: AccessTCI is not a known placeholder")

        for blob in LONG_HEX.findall(line):
            if blob.upper() not in allowed_blobs:
                problems.append(f"{where}: long hex value is not a known placeholder")

    return problems


def main(argv: list[str]) -> int:
    """Check every given file.

    Args:
        argv: Paths to check, as pre-commit passes them.

    Returns:
        1 if any file has a violation, otherwise 0.
    """
    problems: list[str] = []
    for name in argv:
        problems.extend(check_file(Path(name)))

    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(
            "\nFixtures must use placeholder identifiers only. "
            "Run 'vtap100 anonymize' or extend the allowlist in "
            "scripts/check_fixture_leaks.py if the value really is an example.",
            file=sys.stderr,
        )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
