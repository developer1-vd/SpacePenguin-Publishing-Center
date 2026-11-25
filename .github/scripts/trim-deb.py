#!/usr/bin/env python3
"""Cuts anything after a .deb's last archive member off, in place.

Some of SpacePenguin's .deb files carry leftover bytes after data.tar (zeros, then
stale data, as when a file is written over a longer one without being cut to
length). dpkg reads only the members the archive lists and ignores them, but
apt's own reader (apt-ftparchive, apt install ./file.deb) stops there. Every
member, and so the package's real contents, stays byte for byte as it was.

    trim-deb.py <file.deb>...
"""
import sys

for path in sys.argv[1:]:
    with open(path, "rb") as f:
        data = f.read()
    if not data.startswith(b"!<arch>\n"):
        sys.exit(f"{path}: not an ar archive")
    end, members = 8, []
    while end + 60 <= len(data) and data[end + 58:end + 60] == b"`\n":
        members.append(data[end:end + 16].decode("ascii", "replace").strip())
        size = int(data[end + 48:end + 58])
        end += 60 + size + (size % 2)
    if members[:1] != ["debian-binary"] or not any(m.startswith("control.tar") for m in members) \
            or not any(m.startswith("data.tar") for m in members) or end > len(data):
        sys.exit(f"{path}: not a complete .deb ({members})")
    if end < len(data):
        with open(path, "r+b") as f:
            f.truncate(end)
        print(f"{path}: cut {len(data) - end} stray bytes after {members[-1]}")
