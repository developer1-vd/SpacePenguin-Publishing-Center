# SpacePenguin for Fedora (dnf)

Two ways, both built from `spacepenguin.spec` in this folder against Fedora's own
Qt.

## Our own dnf repository (Fedora 45 and newer)

Built and signed by the *publish* workflow (packages and repository metadata, with
`RPM-GPG-KEY-spacepenguin`, fingerprint
`0894 7671 2DCF 4881 8FFD  6A8E 635C 6D02 50D9 63DB`) and served by GitHub Pages:

```sh
sudo curl -fsSLo /etc/yum.repos.d/spacepenguin.repo \
    https://developer1-vd.github.io/SpacePenguin-Publishing-Center/rpm/spacepenguin.repo
sudo dnf install spacepenguin
```

dnf asks once to trust the key. It serves a Fedora-built package: the `.rpm` in
SpacePenguin's release may be openSUSE's, which needs a newer Qt than Fedora has.

## COPR

[COPR](https://copr.fedorainfracloud.org) is Fedora's build service: it builds the
package from `spacepenguin.spec` for every Fedora release you choose, on its own
servers. Once it is set up:

```sh
sudo dnf copr enable <your FAS name>/spacepenguin
sudo dnf install spacepenguin
```

### Setting it up (once)

1. Make a [Fedora account](https://accounts.fedoraproject.org) and sign in to
   COPR with it.
2. *New Project*: name `spacepenguin`; chroots `fedora-45-x86_64`,
   `fedora-45-aarch64`, rawhide, and any older Fedora whose Qt is 6.8 or newer
   (a chroot whose Qt is too old fails to build, which is harmless).
3. In the project, *Packages › New package*, source type **SCM**:
   - Clone URL: `https://github.com/developer1-vd/SpacePenguin-Publishing-Center`
   - Spec file: `pub/dnf/spacepenguin.spec`
   - Type: git; SRPM build method: **make srpm** (it runs `.copr/Makefile`, which
     downloads SpacePenguin's source for the spec)
   - Tick *Auto-rebuild*.
4. *Settings › Integrations* gives a webhook URL: add it to this repository
   (*Settings › Webhooks*, content type `application/json`, push events). Then
   COPR rebuilds whenever `spacepenguin.spec` changes here.

### A new version

Change `upstream_version` at the top of `spacepenguin.spec` and add a
`%changelog` entry; the push rebuilds it in COPR. To build it yourself on
Fedora:

```sh
sudo dnf install rpm-build rpmdevtools 'dnf-command(builddep)'
sudo dnf builddep pub/dnf/spacepenguin.spec
spectool -g -R pub/dnf/spacepenguin.spec
rpmbuild -ba pub/dnf/spacepenguin.spec
```

Versions: `1.0.0-rc.7` becomes `1.0.0~rc.7`, which RPM sorts before `1.0.0`, so
release candidates update to the final version.
