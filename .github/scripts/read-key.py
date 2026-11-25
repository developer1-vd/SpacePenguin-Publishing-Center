#!/usr/bin/env python3
"""Turns the REPO_GPG_PRIVATE_KEY secret into an armoured private key for gpg.

Reads the secret from the environment variable named by the first argument and
prints the key on stdout. Pastes into GitHub's secret box get mangled in a few
usual ways, and this undoes them: the line breaks turned into spaces or lost,
Windows line endings, quotes around it, or the whole file base64-encoded.

When it is not a private key it says what it is instead, as a GitHub error, and
never prints any of the secret.
"""
import base64
import binascii
import os
import re
import sys

BEGIN = "-----BEGIN PGP PRIVATE KEY BLOCK-----"
END = "-----END PGP PRIVATE KEY BLOCK-----"


def fail(message):
    print(f"::error::{message}", file=sys.stderr)
    sys.exit(1)


def rewrap(text):
    """The armour between BEGIN and END, rebuilt with proper line breaks."""
    body = text.split(BEGIN, 1)[1].split(END, 1)[0]
    # Drop armour headers such as "Comment: ..." (they hold a colon and a space).
    lines = [l for l in re.split(r"[\r\n]+", body) if not re.match(r"^\s*[A-Za-z-]+: ", l)]
    data = re.sub(r"\s+", "", "".join(lines))
    checksum = ""
    match = re.search(r"=([A-Za-z0-9+/]{4})$", data)
    if match and len(data) % 4 == 1:  # "=XXXX" after the base64 is the checksum
        checksum, data = "=" + match.group(1), data[: match.start()]
    if not re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", data):
        fail("REPO_GPG_PRIVATE_KEY has characters a key cannot hold between its BEGIN "
             "and END lines: paste REPO_GPG_PRIVATE_KEY.txt again, unchanged.")
    try:
        base64.b64decode(data, validate=True)
    except binascii.Error:
        fail("REPO_GPG_PRIVATE_KEY is cut short: paste the whole of REPO_GPG_PRIVATE_KEY.txt, "
             "BEGIN and END lines included.")
    wrapped = "\n".join(data[i:i + 64] for i in range(0, len(data), 64))
    return f"{BEGIN}\n\n{wrapped}\n{checksum + chr(10) if checksum else ''}{END}\n"


def main():
    secret = os.environ.get(sys.argv[1], "").strip().strip("\"'").strip()
    if not secret:
        fail(f"Set the {sys.argv[1]} secret (Settings › Secrets and variables › Actions).")
    if BEGIN not in secret:
        try:
            decoded = base64.b64decode(re.sub(r"\s+", "", secret), validate=True).decode()
        except (binascii.Error, UnicodeDecodeError):
            decoded = ""
        if BEGIN in decoded:
            secret = decoded  # saved base64-encoded; that works too
        elif "BEGIN PGP PUBLIC KEY BLOCK" in secret:
            fail(f"{sys.argv[1]} holds the public key; it needs the private key (REPO_GPG_PRIVATE_KEY.txt).")
        elif "BEGIN PGP SIGNATURE" in secret or "revocation" in secret.lower():
            fail(f"{sys.argv[1]} holds a signature or revocation certificate; it needs the private key "
                 "(REPO_GPG_PRIVATE_KEY.txt).")
        else:
            fail(f"{sys.argv[1]} is not a private key (no BEGIN PGP PRIVATE KEY BLOCK line): paste the "
                 "whole of REPO_GPG_PRIVATE_KEY.txt, BEGIN and END lines included.")
    if END not in secret:
        fail(f"{sys.argv[1]} is cut short (no END PGP PRIVATE KEY BLOCK line): paste the whole of "
             "REPO_GPG_PRIVATE_KEY.txt.")
    if secret.count(BEGIN) > 1:
        fail(f"{sys.argv[1]} holds more than one key: paste only REPO_GPG_PRIVATE_KEY.txt.")
    sys.stdout.write(rewrap(secret))


main()
