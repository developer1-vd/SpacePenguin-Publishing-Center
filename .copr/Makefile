# COPR's "make srpm" build method (pub/dnf/README.md): COPR clones this repository and
# runs `make -f .copr/Makefile srpm outdir=<folder> spec=<spec>` in a Fedora
# container with network access, then builds the source package it leaves there.
spec ?= pub/dnf/spacepenguin.spec
outdir ?= .
sourcedir := $(shell mktemp -d)

srpm:
	dnf -y install rpmdevtools rpm-build
	spectool -g -R --define "_sourcedir $(sourcedir)" "$(spec)"
	rpmbuild -bs --define "_sourcedir $(sourcedir)" --define "_srcrpmdir $(outdir)" "$(spec)"
