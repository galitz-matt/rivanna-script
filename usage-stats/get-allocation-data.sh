if  [ "$#" -ne 3 ]; then
  echo "Usage: `basename $0` YEAR MONTH OUTPUTPATH"
  exit 1
fi

YEAR=$1
MONTH=$2
OUTPUTPATH=$3

echo "2359,Name,0,,Account=natashaironside,76358.562,0.000,100000.000,100000.000,2340:76358.5617:2023-10-01:2024-10-01,,,renewal_2023-10-01-19:29:40,2023-10-01 19:29:40,2023-10-01 19:29:40,False,56651014,358186893" > ${OUTPUTPATH}/allocations-${YEAR}-${MONTH}.csv
sudo /opt/mam/current/bin/mam-list-funds --full --format csv|grep _${YEAR}-${MONTH} >> ${OUTPUTPATH}/allocations-${YEAR}-${MONTH}.csv

sudo /opt/mam/current/bin/mam-list-accounts --full --format csv >> ${OUTPUTPATH}/allocationsaccounts.csv

awk -F'^' '{print $2}' ${OUTPUTPATH}/allocationsaccounts.csv | awk -F'[,"]' '{print $1}' > ${OUTPUTPATH}/allocationPIs.txt
ldapreport.sh ${OUTPUTPATH}/allocationPIs.txt > ${OUTPUTPATH}/allocationPIsFull.csv
ml anaconda
mergeusers.py ${OUTPUTPATH}/allocationPIsFull.csv ${OUTPUTPATH}
ml anaconda
generate-new-mam-allocations.py ${YEAR} ${MONTH} ${OUTPUTPATH}
