#!/bin/bash
set -euo pipefail

SPEC_FILE="$(find . -mindepth 1 -maxdepth 1 -name '*.spec' -printf '%f\n')"
NAME="$(rpmspec -q --srpm --qf '%{NAME}' "${SPEC_FILE}")"
VERSION="$(rpmspec -q --srpm --qf '%{VERSION}' "${SPEC_FILE}")"
OUTPUT="${NAME}-${VERSION}-vendor.tar.bz2"
SOURCES_DIR="${HOME}/rpmbuild/SOURCES"

if [ -f "${SOURCES_DIR}/${OUTPUT}" ]; then
    echo "Vendor tarball already exists: ${OUTPUT}"
    exit 0
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

tar -xf "${SOURCES_DIR}/${NAME}-${VERSION}.tar.gz" -C "${WORK_DIR}"

go_vendor_archive create \
    -c go-vendor-tools.toml \
    -O "${SOURCES_DIR}/${OUTPUT}" \
    "${WORK_DIR}/${NAME}-${VERSION}"
