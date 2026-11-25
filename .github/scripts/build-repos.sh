#!/usr/bin/env bash
# Builds the signed apt and dnf repositories that GitHub Pages serves, from a
# folder that fetch-release.py filled:
#
#   build-repos.sh <folder with manifest.json> <site folder> [folder of .rpm files]
#
# The .rpm files for the dnf repository come from the third folder when given: the
# publish workflow builds them on Fedora from pub/dnf/spacepenguin.spec, because
# the release's own .rpm may be openSUSE's.
#
# The signing key comes from REPO_GPG_PRIVATE_KEY (the armoured private key), or
# from the GnuPG home already set up when it is unset. Needs apt-utils, createrepo-c,
# rpm (for rpmsign) and gnupg.
set -euo pipefail

IN="$(cd "$1" && pwd)"
SITE="$2"
RPMS="$(cd "${3:-$1}" && pwd)"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BASE_URL="https://developer1-vd.github.io/SpacePenguin-Publishing-Center"
VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "${IN}/manifest.json")"

if [[ -n "${REPO_GPG_PRIVATE_KEY:-}" ]]; then
    GNUPGHOME="$(mktemp -d)"
    export GNUPGHOME
    python3 "${ROOT}/.github/scripts/read-key.py" REPO_GPG_PRIVATE_KEY >"${GNUPGHOME}/key.asc"
    gpg --batch --quiet --import "${GNUPGHOME}/key.asc" ||
        { echo "::error::gpg could not read REPO_GPG_PRIVATE_KEY: paste the whole of REPO_GPG_PRIVATE_KEY.txt again." >&2; exit 1; }
    rm -f "${GNUPGHOME}/key.asc"
fi
KEY="$(gpg --list-secret-keys --with-colons | awk -F: '/^fpr/ {print $10; exit}')"
[[ -n "${KEY}" ]] || { echo "No signing key: set REPO_GPG_PRIVATE_KEY" >&2; exit 1; }
# The key in this repository is the one people trust; refuse any other.
PUBLISHED="$(gpg --with-colons --import-options show-only --import "${ROOT}/pub/apt/spacepenguin-archive-keyring.asc" | awk -F: '/^fpr/ {print $10; exit}')"
[[ "${KEY}" == "${PUBLISHED}" ]] || { echo "::error::REPO_GPG_PRIVATE_KEY is the key ${KEY}, not the repositories' key ${PUBLISHED} (is it the Flatpak key?): paste REPO_GPG_PRIVATE_KEY.txt." >&2; exit 1; }

rm -rf "${SITE}"
mkdir -p "${SITE}"

echo "==> apt repository"
APT="${SITE}/apt"
mkdir -p "${APT}/pool/main/s/spacepenguin" "${APT}/dists/stable/main/binary-amd64"
# One .deb: Debian 13's when the release has several (its dependencies are the
# oldest, so it also installs on Ubuntu 26.04 and newer).
DEBS=("${IN}"/*.deb)
for deb in "${DEBS[@]}"; do [[ "${deb}" == *debian* ]] && DEBS=("${deb}") && break; done
cp "${DEBS[0]}" "${APT}/pool/main/s/spacepenguin/"
python3 "${ROOT}/.github/scripts/trim-deb.py" "${APT}"/pool/main/s/spacepenguin/*.deb
for deb in "${APT}"/pool/main/s/spacepenguin/*.deb; do dpkg-deb --contents "${deb}" >/dev/null; done
(
    cd "${APT}"
    apt-ftparchive packages pool >dists/stable/main/binary-amd64/Packages
    gzip -9kn dists/stable/main/binary-amd64/Packages
    apt-ftparchive \
        -o APT::FTPArchive::Release::Origin=SpacePenguin \
        -o APT::FTPArchive::Release::Label=SpacePenguin \
        -o APT::FTPArchive::Release::Suite=stable \
        -o APT::FTPArchive::Release::Codename=stable \
        -o APT::FTPArchive::Release::Architectures=amd64 \
        -o APT::FTPArchive::Release::Components=main \
        -o "APT::FTPArchive::Release::Description=SpacePenguin ${VERSION}" \
        release dists/stable >dists/stable/Release
    gpg --batch --yes --local-user "${KEY}" --clearsign -o dists/stable/InRelease dists/stable/Release
    gpg --batch --yes --local-user "${KEY}" --armor --detach-sign -o dists/stable/Release.gpg dists/stable/Release
)
cp "${ROOT}/pub/apt/spacepenguin-archive-keyring.gpg" "${ROOT}/pub/apt/spacepenguin-archive-keyring.asc" "${APT}/"
cat >"${APT}/spacepenguin.sources" <<EOF
Types: deb
URIs: ${BASE_URL}/apt
Suites: stable
Components: main
Signed-By: /etc/apt/keyrings/spacepenguin-archive-keyring.gpg
EOF

echo "==> dnf repository"
RPM="${SITE}/rpm"
mkdir -p "${RPM}"
find "${RPMS}" -maxdepth 1 -name '*.rpm' ! -name '*.src.rpm' ! -name '*-debug*' -exec cp {} "${RPM}/" \;
rpmsign --define "_gpg_name ${KEY}" --define "__gpg /usr/bin/gpg" --addsign "${RPM}"/*.rpm >/dev/null
rpm -qpi "${RPM}"/*.rpm | grep -E '^(Name|Version|Release|Signature)'
createrepo_c --quiet "${RPM}"
gpg --batch --yes --local-user "${KEY}" --armor --detach-sign -o "${RPM}/repodata/repomd.xml.asc" "${RPM}/repodata/repomd.xml"
cp "${ROOT}/pub/dnf/RPM-GPG-KEY-spacepenguin" "${RPM}/"
cat >"${RPM}/spacepenguin.repo" <<EOF
[spacepenguin]
name=SpacePenguin
baseurl=${BASE_URL}/rpm
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=${BASE_URL}/rpm/RPM-GPG-KEY-spacepenguin
EOF

echo "==> page"
cat >"${SITE}/index.html" <<EOF
<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SpacePenguin packages</title>
<style>
  body { font: 16px/1.5 system-ui, sans-serif; max-width: 46rem; margin: 2rem auto; padding: 0 1rem; color: #1d2433; }
  pre { background: #f1f4f9; padding: .8rem 1rem; border-radius: 8px; overflow-x: auto; }
  @media (prefers-color-scheme: dark) { body { background: #10141c; color: #e6e9ef; } pre { background: #1b2230; } }
</style>
<h1>SpacePenguin packages</h1>
<p>Version ${VERSION}. Signed with the key
<code>${KEY}</code>, also in
<a href="https://github.com/developer1-vd/SpacePenguin-Publishing-Center/tree/main/pub">the publishing center</a>.</p>
<h2>Debian 13, Ubuntu 26.04 and newer (apt)</h2>
<pre>sudo install -d /etc/apt/keyrings
sudo curl -fsSLo /etc/apt/keyrings/spacepenguin-archive-keyring.gpg ${BASE_URL}/apt/spacepenguin-archive-keyring.gpg
sudo curl -fsSLo /etc/apt/sources.list.d/spacepenguin.sources ${BASE_URL}/apt/spacepenguin.sources
sudo apt update &amp;&amp; sudo apt install spacepenguin</pre>
<h2>Fedora 45 and newer (dnf)</h2>
<pre>sudo curl -fsSLo /etc/yum.repos.d/spacepenguin.repo ${BASE_URL}/rpm/spacepenguin.repo
sudo dnf install spacepenguin</pre>
<p>Updates arrive with the system's own updates.</p>
EOF
find "${SITE}" -type f | sort
