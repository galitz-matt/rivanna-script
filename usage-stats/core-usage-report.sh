#!/bin/bash

if [ "$#" -ne 6 ]; then
    echo "Usage: `basename $0` YYYY-MM-DDThh:mm:ss YYYY-MM-DDThh:mm:ss outputfile days-in-period filter outputpath"
    exit 1
fi

today=$(date +%Y-%m-%d)

START=$1
END=$2
OUT_FILE=$3
DAYS=$4
FILTER=$5
OUTPUTPATH="$6"

YYYYMM=`echo $START | cut -c1-7`
STATES="CANCELLED,COMPLETED,FAILED,NODE_FAIL,PREEMPTED,TIMEOUT,OUT_OF_MEMORY"
CORE_USAGE_FILE=${OUTPUTPATH}/rivanna-corehours-${START}-${END}.csv
CAPACITY_FILE=${OUTPUTPATH}/rivanna-capacity-${START}-${END}.csv
ALLOC_FILE=${OUTPUTPATH}/rivanna-allocations-$today.txt
ORG_FILE=${OUTPUTPATH}/rivanna-organizations-$today.txt

COLUMNS="user,jobname%30,account%50,cputimeraw,alloctres,alloccpus,partition,reserved,state"
LABELS="${COLUMNS/"account%50"/Allocation}" 
LABELS="${LABELS/"jobname%30"/JobName}"
echo "$LABELS" | tr \, \| > $CORE_USAGE_FILE
TZ=UTC sacct -P -n -a -X -S ${START} -E ${END} -s ${STATES} --format=${COLUMNS} >> $CORE_USAGE_FILE
sed -i 's/chr.*slurm/chr slurm/g' $CORE_USAGE_FILE

sinfo -N --format="%R|%N|%T|%c|%G" > $CAPACITY_FILE

sudo /opt/mam/current/bin/mam-list-accounts > $ALLOC_FILE
/opt/mam/current/bin/mam-list-organizations > $ORG_FILE
refactor-orgfile.py $ORG_FILE # refactor organization acronyms

sed -i 's/Health_Volunteer Volunteer sponsored/Health_Volunteer_Volunteer_sponsored/g' $ALLOC_FILE
sed -i 's/Health_Volunteer Volunteer sponsored/Health_Volunteer_Volunteer_sponsored/g' $ORG_FILE

# create summary
core-usage-summary.py -d $DAYS -c $CAPACITY_FILE -u $CORE_USAGE_FILE -x $ORG_FILE -a $ALLOC_FILE -l "$LABELS" -p "${OUTPUTPATH}/{FILTER}/${YYYYMM}" -o $OUT_FILE -g "PI,School|Allocation,Description,PI,School|Allocation,Description,PI,School,partition|School,Organization|user,School|Allocation,user,PI,School,Organization|user,Allocation,PI,School,Organization|School|School,JobType|School,partition|School,partition,JobType" -f "${FILTER}"
