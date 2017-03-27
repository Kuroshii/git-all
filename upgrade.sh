#!/bin/bash -e
NAME="git-all"
LIB_FOLDER=$1

rm -rf $LIB_FOLDER/$NAME/src
mkdir -p $LIB_FOLDER/$NAME/src
cp -r src/ $LIB_FOLDER/$NAME/src
