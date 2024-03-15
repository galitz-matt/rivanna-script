#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: `basename $0` YYYY MM outputfile outputpath"
    exit 1
fi

date=$(date '+%Y-%m-%d')

YEAR=$1
MONTH=$2
OUTPUTFILE=$3 # joined w/ output path
OUTPUTPATH=$4

FIRSTDAY=$(date -d "$YEAR/$MONTH/1" "+%Y-%m-%d")
LASTDAY=$(date -d "$FIRSTDAY + 1 month " "+%Y-%m-%d")
#LASTDAY=$(date -d "$FIRSTDAY + 1 year " "+%Y-%m-%d")
echo "New users in $YEAR/$MONTH"
echo $FIRSTDAY - $LASTDAY

SUFFIX=${YEAR}-${MONTH}
USERIDS=${OUTPUTPATH}/newUIDs-${SUFFIX}.txt
echo Getting new accounts
mam-list-users --full -A --format=csv | awk -F"," -v FIRST=$FIRSTDAY -v LAST=$LASTDAY '{ if ($2=="True" && $8>=FIRST && $8<LAST) { print $1 } }' > $USERIDS
echo New UIDs saved in $USERIDS

echo Searching LDAP
echo Done.
echo ---------------------------------

ldapreport.sh $USERIDS > $OUTPUTFILE

mergeusers.py $OUTPUTFILE $OUTPUTPATH
