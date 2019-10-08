#!/bin/bash

# Add to PATH.
D="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" >/dev/null 2>&1 && pwd )"
echo "export PATH=\$PATH:$D" >> ~/.bashrc


# For scripts.
sudo apt install python3 python3-bibtexparser python3-requests

# DB Browser for SQLite
sudo apt install git build-essential cmake libqt4-dev libsqlite3-dev
git clone https://github.com/MilosSubotic/sqlitebrowser
pushd sqlitebrowser
git checkout file_name_stuff
cmake .
make -j4
sudo make install
popd
