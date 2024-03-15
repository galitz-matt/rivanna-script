#!/bin/bash

if [ "$#" -ne 5 ]; then
    echo "Usage: `basename $0` YYYY MM DAYS FILTER OUTPUTPATH"
    exit 1
fi

SYEAR=$1
SMONTH=$2
DAYS=$3
FILTER=$4 
OUTPUTPATH=$5

SDAY=01
FIRSTDAYMONTH=${SYEAR}-${SMONTH}-${SDAY}
FIRSTNEXTMONTH=$(date -d "${SYEAR}${SMONTH}${SDAY}+1 month" +%Y-%m-%d)
LASTDAYMONTH=$(date -d "${FIRSTNEXTMONTH}-1 day" +%Y-%m-%d)
echo "Reporting $FIRSTDAYMONTH through $LASTDAYMONTH"
echo "Writing to $OUTPUTPATH"
echo "Filtering: $FILTER"

newusers-report.sh ${SYEAR} ${SMONTH} ${OUTPUTPATH}/newusers-${SYEAR}-${SMONTH}.csv ${OUTPUTPATH}

get-allocation-data.sh ${SYEAR} ${SMONTH} ${OUTPUTPATH}

core-usage-report.sh ${FIRSTDAYMONTH}T00:00:00 ${LASTDAYMONTH}T23:59:59 corehours-${SYEAR}-${SMONTH}.csv $DAYS "${FILTER}" $OUTPUTPATH

awk -F, '{ if ($2 > 0) print $1 }' ${OUTPUTPATH}/all/${SYEAR}-${SMONTH}/corehours-${SYEAR}-${SMONTH}-userSchool-all.csv | sort -u > ${OUTPUTPATH}/activeusers-UIDs-${SYEAR}-${SMONTH}.txt
ldapreport.sh ${OUTPUTPATH}/activeusers-UIDs-${SYEAR}-${SMONTH}.txt > ${OUTPUTPATH}/activeusers-${SYEAR}-${SMONTH}.csv
mergeusers.py ${OUTPUTPATH}/activeusers-${SYEAR}-${SMONTH}.csv ${OUTPUTPATH}
