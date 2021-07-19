#! /bin/bash

export DATA_PATH=/shared/behavioral_data
export OUT_PATH=/shared/bids_nifti_wface
export CODE_PATH=/shared/01_bidsify

aws s3 sync s3://described-vs-experienced/behavioral_data $DATA_PATH
if [[ ! -e $OUT_PATH ]]; then
  mkdir $OUT_PATH
fi
aws s3 sync s3://described-vs-experienced/01_bidsify $CODE_PATH

chown -R ec2-user: $DATA_PATH
chown -R ec2-user: $OUT_PATH
chown -R ec2-user: $CODE_PATH

pip3 install scipy -U --user
pip3 install pandas -U --user
