#!/usr/bin/env python3
"""Writes pub/win, pub/macos and pub/android's README.md for a published version:
its files, with their sizes, checksums and download links in this repository's
release.

    write-listings.py <folder with manifest.json> <repository root>
"""
import json
import pathlib
import sys

REPO = "developer1-vd/SpacePenguin-Publishing-Center"
TITLES = {
    "win": ("Windows", "Run the installer; it installs for you alone, or for everyone "
            "with administrator rights. The zip runs without installing. Windows "
            "SmartScreen may warn the first time: *More info › Run anyway*."),
    "macos": ("macOS", "Open the disk image and drag SpacePenguin to Applications. It is "
              "not notarised yet, so the first start needs *System Settings › Privacy "
              "& Security › Open Anyway*. Or with Homebrew: `brew tap "
              "developer1-vd/spacepenguin && brew trust developer1-vd/spacepenguin && "
              "brew install --cask spacepenguin`."),
    "android": ("Android", "Open the APK on the phone and allow installing from your "
                "browser or files app, or `adb install -r` it."),
}


def main():
    manifest = json.loads((pathlib.Path(sys.argv[1]) / "manifest.json").read_text())
    root = pathlib.Path(sys.argv[2])
    version = manifest["version"]
    base = f"https://github.com/{REPO}/releases/download/v{version}"
    for platform, (title, how) in TITLES.items():
        lines = [
            f"# SpacePenguin for {title}",
            "",
            f"**Version {version}**{' (release candidate)' if manifest['prerelease'] else ''}, "
            f"from [SpacePenguin's release]({manifest['source']}).",
            "",
            how,
            "",
            "| File | What it is | Size | SHA-256 |",
            "| ---- | ---------- | ---- | ------- |",
        ]
        for f in manifest["files"]:
            if f["platform"] == platform:
                lines.append(f"| [{f['name']}]({base}/{f['name']}) | {f['label']} "
                             f"| {f['size'] / 1e6:.0f} MB | `{f['sha256']}` |")
        lines += [
            "",
            "The files are in this repository's "
            f"[v{version} release](https://github.com/{REPO}/releases/tag/v{version}), "
            "copied there by the *publish* workflow and checked against SpacePenguin's.",
            "Check a download with `sha256sum <file>` (Linux), `shasum -a 256 <file>` "
            "(macOS) or `Get-FileHash <file>` (Windows).",
            "",
        ]
        (root / "pub" / platform / "README.md").write_text("\n".join(lines))
        print(f"pub/{platform}/README.md")


if __name__ == "__main__":
    main()
