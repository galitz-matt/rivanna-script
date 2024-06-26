#!/bin/bash

# Configured to report utilization data of prior month
year=$(date --date="$(date +%Y-%m-15) -1 month" +%Y)
month=$(date --date="$(date +%Y-%m-15) -1 month" +%m)
last_day=$(date -d "$year-$month-01 +1 month -1 day" +%d)

filter="" # TODO: Change to desired filter
output_dir="/path/to/output/dir" # TODO: Change to output directory where reports will be stored
conda_env="/path/to/conda/env" # TODO: Change to conda env created by install.sh

SCRIPT="/absolute/path/to/monthly-report.sh" # TODO: Change this to the actual full path

ml anaconda
source activate $conda_env
$SCRIPT $year $month $last_day $filter $output_dir
conda deactivate
module unload anaconda
