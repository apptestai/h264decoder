#!/usr/bin/env bash

set -x

TARGET=$1

if [ -z "$TARGET" ]
then
    TARGET=.
fi

mypy $TARGET
pylint --rcfile .pylintrc $TARGET