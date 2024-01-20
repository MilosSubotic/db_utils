#!/bin/bash
###############################################################################
# Check is this Ubuntu.

DIST=`lsb_release --id | sed 's/^Distributor ID:[\t ]*\(.*\)$/\1/'`
if [[ "$DIST" != "Ubuntu" ]]
then
	echo "This install script is made for Ubuntu GNU/Linux distribution!"
	echo "You need to change it a little for your distribution!"
	exit 1
fi

R=`lsb_release --release`
MAJOR=`echo $R | sed -n 's/^Release:[\t ]*\([0-9]\+\)\.\([0-9]\+\)$/\1/p'`

###############################################################################
# For scripts.

if (( $MAJOR < 20 ))
then
	# scholarly need Ubuntu 20
	echo "Not supported version of Ubuntu!"
	exit 1
fi
sudo apt -y install python3-bibtexparser python3-requests python3-openpyxl
sudo apt -y install python3-pip
sudo pip3 install scholarly

###############################################################################
# DB Browser for SQLite.

sudo apt -y install git build-essential cmake libsqlite3-dev libsqlcipher-dev
sudo apt -y install qtbase5-dev qt5-qmake qttools5-dev-tools \
	qtbase5-dev libqt5scintilla2-dev libqcustomplot-dev qttools5-dev
git clone https://github.com/MilosSubotic/sqlitebrowser
pushd sqlitebrowser
git checkout file_name_stuff_qt5
mkdir build && cd build
cmake -Dsqlcipher=1 -Wno-dev ..
make -j4
sudo make install
popd
rm -rf sqlitebrowser

###############################################################################
