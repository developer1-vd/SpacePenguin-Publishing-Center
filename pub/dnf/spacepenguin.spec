# SpacePenguin for Fedora, built by COPR (or rpmbuild) against Fedora's own Qt.
# pub/dnf/README.md says how to set up the COPR project that builds it.
#
# For a new release, change upstream_version, add a %changelog entry, and let COPR
# rebuild (or pass --define "upstream_version 1.0.0-rc.8" to rpmbuild, as the
# publish workflow does). Release candidates become 1.0.0~rc.7, which RPM sorts
# before 1.0.0.

%{!?upstream_version:%global upstream_version 1.0.0-rc.7}

Name:           spacepenguin
Version:        %(echo %{upstream_version} | tr - '~')
Release:        1%{?dist}
Summary:        Secure, lightweight browser built on Qt and Chromium

License:        GPL-3.0-or-later
URL:            https://github.com/developer1-vd/SpacePenguin
Source0:        %{url}/archive/refs/tags/v%{upstream_version}/SpacePenguin-%{upstream_version}.tar.gz

# QtWebEngine (Chromium) is built for these only.
ExclusiveArch:  x86_64 aarch64

BuildRequires:  cmake >= 3.21
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  cmake(Qt6Core) >= 6.8
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6Network)
BuildRequires:  cmake(Qt6WebEngineWidgets) >= 6.8
BuildRequires:  cmake(Qt6LinguistTools)
BuildRequires:  qt6-qtwayland-devel
BuildRequires:  libglvnd-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       hicolor-icon-theme
Provides:       webclient

%description
SpacePenguin is a small, fast web browser built on Qt and QtWebEngine
(Chromium). It blocks ads and trackers, YouTube's included, skips sponsor
segments, keeps to HTTPS, and has private and Tor windows, a translator,
Read Aloud, Picture-in-Picture and roles for students, teachers, developers
and gamers.

%prep
%autosetup -n SpacePenguin-%{upstream_version}

%build
# Fedora confines programs with SELinux, not AppArmor, so no AppArmor profile.
%cmake -G Ninja \
    -DSPACEPENGUIN_USE_LOCAL_QT=OFF \
    -DSPACEPENGUIN_INSTALL_QT_CONF=OFF \
    -DSPACEPENGUIN_INSTALL_APPARMOR_PROFILE=OFF \
    -DSPACEPENGUIN_BUILD_TESTS=OFF
%cmake_build

%install
%cmake_install

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/io.github.developer1_vd.SpacePenguin.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/io.github.developer1_vd.SpacePenguin.metainfo.xml

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/SpacePenguin
%{_datadir}/applications/io.github.developer1_vd.SpacePenguin.desktop
%{_metainfodir}/io.github.developer1_vd.SpacePenguin.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/io.github.developer1_vd.SpacePenguin.png

%changelog
* Tue Nov 24 2026 SpacePenguin <spacepenguin@users.noreply.github.com> - 1.0.0~rc.7-1
- SpacePenguin 1.0.0-rc.7: https://github.com/developer1-vd/SpacePenguin/releases/tag/v1.0.0-rc.7
