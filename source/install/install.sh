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
	# New python3.
	sudo add-apt-repository -y ppa:deadsnakes/ppa
	sudo apt update
	sudo apt install -y python3.7
	sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 5
	sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 7
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

###############################################################################
# DB Browser for SQLite.

sudo apt install -y git build-essential cmake libqt4-dev libsqlite3-dev
git clone https://github.com/MilosSubotic/sqlitebrowser
pushd sqlitebrowser
git checkout file_name_stuff
cmake .
make -j4
sudo make install
popd

###############################################################################
