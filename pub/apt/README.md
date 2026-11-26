# SpacePenguin for Debian and Ubuntu (apt)

Two ways, both kept up to date by the *publish* workflow.

## Our own apt repository (Debian 13, Ubuntu 26.04 and newer)

Signed with the key in this folder (`spacepenguin-archive-keyring.gpg`,
fingerprint `0894 7671 2DCF 4881 8FFD  6A8E 635C 6D02 50D9 63DB`) and served by
GitHub Pages:

```sh
sudo install -d /etc/apt/keyrings
sudo curl -fsSLo /etc/apt/keyrings/spacepenguin-archive-keyring.gpg \
    https://developer1-vd.github.io/SpacePenguin-Publishing-Center/apt/spacepenguin-archive-keyring.gpg
sudo curl -fsSLo /etc/apt/sources.list.d/spacepenguin.sources \
    https://developer1-vd.github.io/SpacePenguin-Publishing-Center/apt/spacepenguin.sources
sudo apt update && sudo apt install spacepenguin
```

It serves the `.deb` from SpacePenguin's release, after cutting off stray bytes
some of them carry at the end (`.github/scripts/trim-deb.py`), which apt refuses.

## The PPA (Ubuntu 26.04)

Launchpad builds SpacePenguin on its own servers from the source package that
`make-source.sh` makes from this folder's `debian/`. Once it is set up:

```sh
sudo add-apt-repository ppa:developer1xd/spacepenguin
sudo apt install spacepenguin
```

Ubuntu 26.04 is the first with the Qt 6.8 SpacePenguin needs, so the PPA builds for
26.04 (`resolute`) and later.

### Setting it up (once)

1. Make an account on [Launchpad](https://launchpad.net) and add an OpenPGP key to
   it (*OpenPGP keys* on your profile). Launchpad only takes uploads signed with a
   key it knows.
2. Sign the Ubuntu Code of Conduct (also on your profile).
3. Create a PPA named `spacepenguin` (*Create a new PPA*), with amd64 and arm64.
4. In this repository's *Settings › Secrets and variables › Actions*:
   - secret `LAUNCHPAD_GPG_PRIVATE_KEY`: that key's private half
     (`gpg --armor --export-secret-keys <key ID>`), without a passphrase;
   - variable `LAUNCHPAD_PPA`: `ppa:developer1xd/spacepenguin`.

From then on, the *publish* workflow uploads each version to the PPA. Launchpad
emails you when it has built (about an hour).

### By hand

```sh
sudo apt install devscripts debhelper dput
DEBSIGN_KEYID=<your key ID> pub/apt/make-source.sh 1.0.0-rc.7
dput ppa:developer1xd/spacepenguin pub/apt/out/*_source.changes
```

A second upload of the same version needs a higher revision:
`make-source.sh 1.0.0-rc.7 resolute 2`.

## What is in this folder

| | |
| - | - |
| `debian/` | the Debian packaging Launchpad builds from (against Ubuntu's own Qt, with the AppArmor profile Chromium's sandbox needs) |
| `make-source.sh` | makes the source package for a version from SpacePenguin's tagged source |
| `spacepenguin-archive-keyring.gpg`, `.asc` | the public key that signs our apt repository |

Versions: `1.0.0-rc.7` becomes `1.0.0~rc.7`, which Debian sorts before `1.0.0`,
so release candidates update to the final version.
