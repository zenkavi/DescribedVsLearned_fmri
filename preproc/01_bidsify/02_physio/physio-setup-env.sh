#! /bin/bash

export DATA_PATH=/shared
export CODE_PATH=/shared/01_bidsify

aws s3 sync s3://described-vs-experienced/raw_fmri_data $DATA_PATH/raw_fmri_data --exclude "*" --include "*.puls" --include "*.ext" --include "*.resp"
aws s3 sync s3://described-vs-experienced/bids_nifti_wface $DATA_PATH/bids_nifti_wface --exclude "*" --include "*_bold.json"

aws s3 sync s3://described-vs-experienced/01_bidsify $CODE_PATH

chown -R ec2-user: $DATA_PATH
chown -R ec2-user: $CODE_PATH
