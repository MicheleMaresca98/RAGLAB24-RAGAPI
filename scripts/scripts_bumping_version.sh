#!/bin/bash

set -eux

new_version_tag=$1
BASE_DIR=$(cd "$(dirname "$0")/.." && pwd)
#
VERSION_FILE_PATH="${BASE_DIR}/questionnaires_compiler/src/django_core/versioninfo.py"



[ ! -d "${BASE_DIR}/.git" ] && { echo "${BASE_DIR} directory doesn't contain .git" >&2; return 1; }

rm_tag_prefix() {
    echo "${1}" | sed "s|^[^0-9]*\([0-9.]*.*\)|\1|"
}

version_tag=$(rm_tag_prefix "$new_version_tag")

sed -i -e "s/\(VERSION: str = [\"']\)\(.*\)\([\"'].*\)/\1${version_tag}\3/" "${VERSION_FILE_PATH}"

VERSION_FILE_PATH2="${BASE_DIR}/questionnaires_compiler/docs/openapi.yaml"
VERSION_FILE_PATH3="${BASE_DIR}/questionnaires_compiler/docs/openapi_integrators.yaml"

sed -i -e "s/\(version: [\"']\)\(.*\)\([\"'].*\)/\1${version_tag}\3/" "${VERSION_FILE_PATH2}"
sed -i -e "s/\(version: [\"']\)\(.*\)\([\"'].*\)/\1${version_tag}\3/" "${VERSION_FILE_PATH3}"

git add "${VERSION_FILE_PATH}"
git add "${VERSION_FILE_PATH2}"
git add "${VERSION_FILE_PATH3}"
git commit -m "docs(version): bump version to ${new_version_tag}"
