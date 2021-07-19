#! /bin/bash

export DATA_PATH=/shared/bids_nifti_wface

aws s3 sync $DATA_PATH s3://described-vs-experienced/bids_nifti_wface
