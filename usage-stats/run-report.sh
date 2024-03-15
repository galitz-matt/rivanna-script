#!/bin/bash

if [ "$#" -ne 5 ]; then
    echo "Usage: `basename $0` YYYY MM DAYS FILTER OUTPUTPATH"
    exit 1
fi

SYEAR=$1
SMONTH=$2
DAYS=$3
FILTER=$4 # new assignment
OUTPUTPATH=$5

source venv/bin/activate

monthly-report.sh $SYEAR $SMONTH $DAYS $FILTER $OUTPUTPATH

deactivate
