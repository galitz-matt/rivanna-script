#!/bin/bash

# update condition to account for FILTER arg
if [ "$#" -ne 5 ]; then
    echo "Usage: `basename $0` YYYY MM DAYS FILTER OUTPUTPATH"
    exit 1
fi

YEAR=$1
MONTH=$2
DAYS=$3
FILTER=$4
OUTPUT=$5

source venv/bin/activate

monthly-report.sh $YEAR $MONTH $DAYS $FILTER $OUTPUT 

deactivate
