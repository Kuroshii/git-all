#!/bin/bash -e

NAME="git-all"
BIN_FOLDER=$1
LIB_FOLDER=$2

# Move source code over
mkdir -p $LIB_FOLDER/$NAME/src
mkdir -p $LIB_FOLDER/$NAME/conf
cp -r src/ $LIB_FOLDER/$NAME/src

# set up virtual environment and requirements
virtualenv -p $(which python3) $LIB_FOLDER/$NAME/venv
source $LIB_FOLDER/$NAME/venv/bin/activate
pip3 install -r requirements.txt

# make a start script
echo "#!/bin/bash -e
LIB_DIR=$LIB_FOLDER" > $BIN_FOLDER/$NAME
cat start-stub >> $BIN_FOLDER/$NAME
chmod +x $BIN_FOLDER/$NAME

# make an uninstall script
echo "#!/bin/bash -e

rm -rf $LIB_FOLDER/$NAME
rm $BIN_FOLDER/$NAME" > $LIB_FOLDER/$NAME/uninstall.sh
chmod +x $LIB_FOLDER/$NAME/uninstall.sh
