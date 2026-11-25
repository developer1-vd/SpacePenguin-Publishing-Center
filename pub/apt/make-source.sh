#!/usr/bin/env bash
# Makes the Ubuntu source package for a SpacePenguin release, which is what a
# Launchpad PPA builds from:
#
#   pub/apt/make-source.sh 1.0.0-rc.7 [series] [revision]
#
# series is the Ubuntu release to build for (default resolute, 26.04: the first
# with the Qt 6.8 SpacePenguin needs); revision counts uploads of the same version
# (default 1). The package goes to pub/apt/out/. It is signed with your key when
# DEBSIGN_KEYID is set (as Launchpad requires), otherwise left unsigned.
#
# Needs devscripts, debhelper and curl (sudo apt install devscripts debhelper curl).
set -euo pipefail

VERSION="${1:?usage: $0 <version, e.g. 1.0.0-rc.7> [series] [revision]}"
VERSION="${VERSION#v}"
[[ "${VERSION}" =~ ^[0-9]+(\.[0-9]+)+(-[0-9A-Za-z.]+)?$ ]] || { echo "Not a version: ${VERSION}" >&2; exit 1; }
SERIES="${2:-resolute}"
REVISION="${3:-1}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${HERE}/out"
# Debian sorts "~" before anything, so 1.0.0~rc.7 comes before 1.0.0.
UPSTREAM="${VERSION//-/\~}"
PACKAGE_VERSION="${UPSTREAM}-${REVISION}~${SERIES}1"

rm -rf "${OUT}"
mkdir -p "${OUT}"
cd "${OUT}"
echo "==> Downloading SpacePenguin ${VERSION}"
curl -fsSL -o "spacepenguin_${UPSTREAM}.orig.tar.gz" \
    "https://github.com/developer1-vd/SpacePenguin/archive/refs/tags/v${VERSION}.tar.gz"
mkdir "spacepenguin-${UPSTREAM}"
tar -xzf "spacepenguin_${UPSTREAM}.orig.tar.gz" -C "spacepenguin-${UPSTREAM}" --strip-components=1
cp -r "${HERE}/debian" "spacepenguin-${UPSTREAM}/debian"

cat >"spacepenguin-${UPSTREAM}/debian/changelog" <<EOF
spacepenguin (${PACKAGE_VERSION}) ${SERIES}; urgency=medium

  * SpacePenguin ${VERSION}:
    https://github.com/developer1-vd/SpacePenguin/releases/tag/v${VERSION}

 -- ${DEBFULLNAME:-SpacePenguin} <${DEBEMAIL:-spacepenguin@users.noreply.github.com}>  $(date -R)
EOF

echo "==> Building the source package ${PACKAGE_VERSION}"
cd "spacepenguin-${UPSTREAM}"
if [[ -n "${DEBSIGN_KEYID:-}" ]]; then
    dpkg-buildpackage -S -sa -d -k"${DEBSIGN_KEYID}"
else
    dpkg-buildpackage -S -sa -d -us -uc
fi
cd "${OUT}"
ls -l "${OUT}"
echo
echo "Upload with: dput ppa:<your Launchpad name>/spacepenguin ${OUT}/spacepenguin_${PACKAGE_VERSION}_source.changes"
