#!/bin/bash

sudo apt install sqlite3
sqldiff papers.sqlite papers_changed.sqlite

grep 'Citation' Main.log | sed 's/.*`\(.*\)\x27.*/\1/p' | sort | uniq > lacking_refs.txt
