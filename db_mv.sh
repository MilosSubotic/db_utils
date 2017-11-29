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
	FIND_RES=$(find "$D" -maxdepth 1 -type d -name db_utils)
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
done

"$D/db_utils/mv_papers.py" "$@"

exit $?

###############################################################################

