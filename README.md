# SpacePenguin Publishing Center

Where [SpacePenguin](https://github.com/developer1-vd/SpacePenguin)'s releases go
out to each platform. The *publish* workflow (Actions › publish › Run workflow,
with a version such as `1.0.0-rc.7`) does it all for a release that is out:

| Folder | What it holds | Where people get it |
| ------ | ------------- | ------------------- |
| [`pub/win`](pub/win) | the Windows installer and zip | this repository's releases |
| [`pub/macos`](pub/macos) | the macOS disk image and zip | this repository's releases, or Homebrew ([homebrew-spacepenguin](https://github.com/developer1-vd/homebrew-spacepenguin)) |
| [`pub/android`](pub/android) | the Android app | this repository's releases |
| [`pub/apt`](pub/apt) | Debian packaging for the PPA, and our apt repository's key | our apt repository, or the PPA |
| [`pub/dnf`](pub/dnf) | the RPM spec for COPR, and our dnf repository's key | our dnf repository, or COPR |
| [`pub/appstore`](pub/appstore) | the App Store listing for the iPhone app | the App Store, once submitted |

Binaries are not kept in Git: GitHub refuses files over 100 MB, and the macOS disk
image is larger. Each version's files are in a [release](../../releases) of this
repository instead, checked against SpacePenguin's own SHA-256 sums; each `pub/`
folder's README lists them.

The apt and dnf repositories are served at
<https://developer1-vd.github.io/SpacePenguin-Publishing-Center/>.

## Setting up (once)

1. *Settings › Pages › Source*: **GitHub Actions**.
2. *Settings › Secrets and variables › Actions*, secret `REPO_GPG_PRIVATE_KEY`:
   the private key that signs the apt and dnf repositories (its public half is in
   `pub/apt` and `pub/dnf`).
3. Optional: the Launchpad secret and variable for the PPA (`pub/apt/README.md`),
   and the COPR project (`pub/dnf/README.md`).

## Licence

GPL-3.0, like SpacePenguin.
