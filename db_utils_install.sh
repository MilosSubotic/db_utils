#!/bin/bash

sudo apt install python3 python3-bibtexparser python3-requests

# DB Browser for SQLite
git clone https://github.com/MilosSubotic/sqlitebrowser
git checkout file_name_stuff
sudo apt install build-essential cmake libqt4-dev libsqlite3-dev
cmake .
make
sudo make install
