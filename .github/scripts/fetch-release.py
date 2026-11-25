#!/usr/bin/env python3
"""Downloads a SpacePenguin release's packages and checks each against the SHA-256
GitHub keeps for it.

    fetch-release.py 1.0.0-rc.7 <folder>

Writes the files and <folder>/manifest.json, which says what each file is for.
GITHUB_TOKEN, when set, is used for GitHub's API (a higher rate limit).
"""
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.request

REPO = "developer1-vd/SpacePenguin"

# What goes where, by file name.
KINDS = [
    ("-windows-x64-setup.exe", "win", "Windows installer (x64)"),
    ("-windows-x64.zip", "win", "Windows portable zip (x64)"),
    ("-macos.dmg", "macos", "macOS disk image (Apple Silicon and Intel)"),
    ("-macos.zip", "macos", "macOS zip (Apple Silicon and Intel)"),
    ("-android-arm64.apk", "android", "Android app (arm64)"),
    ("-ios-unsigned.ipa", "appstore", "iPhone app, unsigned (for sideloading)"),
    (".deb", "apt", "Debian and Ubuntu package"),
    (".rpm", "dnf", "Fedora and openSUSE package"),
]


def api(path):
    request = urllib.request.Request(f"https://api.github.com/{path}",
                                     headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def kind_of(name):
    if "-debug" in name or name.endswith(".sha256"):
        return None
    for suffix, platform, label in KINDS:
        if name.endswith(suffix):
            return platform, label
    return None


def main():
    version = sys.argv[1].removeprefix("v")
    if not re.fullmatch(r"\d+(\.\d+)+(-[0-9A-Za-z.]+)?", version):
        sys.exit(f"{version!r} is not a version such as 1.0.0 or 1.0.0-rc.7")
    folder = pathlib.Path(sys.argv[2])
    folder.mkdir(parents=True, exist_ok=True)
    release = api(f"repos/{REPO}/releases/tags/v{version}")
    files = []
    for asset in release["assets"]:
        kind = kind_of(asset["name"])
        if not kind:
            continue
        digest = asset.get("digest") or ""
        if not digest.startswith("sha256:"):
            sys.exit(f"{asset['name']}: GitHub has no SHA-256 for it")
        expected = digest.removeprefix("sha256:")
        target = folder / asset["name"]
        print(f"Downloading {asset['name']} ({asset['size'] / 1e6:.1f} MB)", flush=True)
        sha = hashlib.sha256()
        with urllib.request.urlopen(asset["browser_download_url"]) as response, open(target, "wb") as out:
            while chunk := response.read(1 << 20):
                sha.update(chunk)
                out.write(chunk)
        if sha.hexdigest() != expected:
            target.unlink()
            sys.exit(f"{asset['name']}: SHA-256 {sha.hexdigest()} is not GitHub's {expected}")
        files.append({"name": asset["name"], "platform": kind[0], "label": kind[1],
                      "size": asset["size"], "sha256": expected})
    for platform in ("win", "macos", "android", "apt", "dnf"):
        if not any(f["platform"] == platform for f in files):
            sys.exit(f"The release has no file for {platform}")
    manifest = {"version": version, "prerelease": release["prerelease"],
                "published": release["published_at"], "source": release["html_url"], "files": files}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{len(files)} files, all matching GitHub's checksums")


if __name__ == "__main__":
    main()
