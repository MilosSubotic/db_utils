#!/bin/bash
###############################################################################
# Add to PATH.

I=`dirname "${BASH_SOURCE[0]}"`
P="`cd "$I/.." >/dev/null 2>&1 && pwd`"
echo "export PATH=\$PATH:$P" >> ~/.bashrc

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

if (( $MAJOR <= 16 ))
then
	# Newer python3 for scholarly to work.
	sudo add-apt-repository -y ppa:deadsnakes/ppa
	sudo apt update
	sudo apt install -y python3.7
	sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 5
	sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 7
	# Patch for gnome-terminal to work on Python3.7
	sudo ln -s /usr/lib/python3/dist-packages/gi/_gi.cpython-{35m,37m}-x86_64-linux-gnu.so
	# pip
	sudo apt install -y python3.7-distutils
	wget https://bootstrap.pypa.io/get-pip.py
	sudo python3 get-pip.py
	rm get-pip.py
else
	sudo apt install -y python3
fi
sudo apt install -y python3-bibtexparser python3-requests
sudo pip3 install scholarly
# Hack for old python3.5 dist-packages
sudo pip3 install --ignore-installed lxml requests
sudo pip3 install FreeProxy

###############################################################################
# DB Browser for SQLite.

sudo apt install -y git build-essential cmake libsqlite3-dev libsqlcipher-dev
sudo apt install -y qt5-default qttools5-dev-tools \
	qtbase5-dev libqt5scintilla2-dev libqcustomplot-dev qttools5-dev
git clone https://github.com/MilosSubotic/sqlitebrowser
pushd sqlitebrowser
git checkout file_name_stuff_qt5
cmake -Dsqlcipher=1 -Wno-dev .
make -j4
sudo make install
popd

###############################################################################
