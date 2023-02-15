#!/usr/bin/env bash

readonly PROGNAME=`basename "$0"`
readonly PROGDIR=`dirname "$0"`
readonly BASEDIR=`dirname "$PROGDIR"`

# set -e
# set -x

rm -r "${BASEDIR}/dist"
rm -r "${BASEDIR}/build"
poetry build -vv