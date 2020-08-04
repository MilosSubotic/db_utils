#!/bin/bash

sudo apt install sqlite3

sqldiff papers.sqlite papers_changed.sqlite
