#! /bin/bash

export DATA_PATH=/shared

aws s3 sync $DATA_PATH/bids_nifti_wface s3://described-vs-experienced/bids_nifti_wface
