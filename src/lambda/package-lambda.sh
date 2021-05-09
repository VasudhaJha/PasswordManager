#!/bin/bash
# Creates zip archive of a lambda to be uploaded to s3, returns the path to the file
# Usage: ./package-lambda.sh LAMBDA_NAME SOURCE_PATH
# Ex. ./package-lambda.sh signup ./user/signup

if [[ $# -ne 2 ]]
then
    echo "2 parameters required, LAMBDA_NAME SOURCE_PATH"
    exit 1
fi

LAMBDA_NAME="$1"
SOURCE_PATH="$2"

S3_KEY="$LAMBDA_NAME.zip"
LAMBDA_FILE_PATH="/tmp/$S3_KEY"
PKG_DIR=/tmp/package
REQUIREMENTS_FILE="$SOURCE_PATH/requirements.txt"

mkdir -p "$PKG_DIR"
cp "$SOURCE_PATH"/* "$PKG_DIR"/

if [[ -f "$REQUIREMENTS_FILE" ]]
then
    VENV_DIR=/tmp/venv
    # shellcheck disable=SC1090
    python3 -m venv "$VENV_DIR" && . "$VENV_DIR/bin/activate"
    if [[ $VIRTUAL_ENV == "" ]]
    then
        echo "Virtual Environment didn't activate, exiting."
        exit 1
    fi

    pip install --upgrade pip > /dev/null 2>&1
    pip install -r "$REQUIREMENTS_FILE" > /dev/null 2>&1

    cp -r --dereference "$VENV_DIR"/lib/*/site-packages/. "$PKG_DIR"

    deactivate destructive

    rm -rf "$VENV_DIR"
fi

if [[ -f "$LAMBDA_FILE_PATH" ]]
then
    rm -f "$LAMBDA_FILE_PATH"
fi

pushd "$PKG_DIR" > /dev/null 2>&1 || return
zip -q -r "$LAMBDA_FILE_PATH" .
popd > /dev/null 2>&1 || return
rm -rf "$PKG_DIR"

echo "$LAMBDA_FILE_PATH"
