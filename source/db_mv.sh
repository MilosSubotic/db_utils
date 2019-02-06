#!/bin/bash
# Move files from hunt place to directory in DB tree and update DB.

# In worker commander add next own command: db_mv.sh {A} {op}
# Set to be: in terminal and wait for key
# Set shortcut to be: Ctrl+F6.
###############################################################################

# Find DB tree directory.
D="${@: -1}"
while true;
do
	FIND_RES=$(find -L "$D" -maxdepth 1 -type f -name *.sqlite)
	if test "$FIND_RES" != ""
	then
		break
	fi
	
	if test "$D" == "/";
	then
		echo "error: not DB tree in destination"
		exit 1
	fi
	
	D=$(dirname "$D")
	#echo $D
done

pushd "$D" 1>/dev/null
mv_papers.py "$@"
R=$?
popd 1>/dev/null

exit $R

###############################################################################
