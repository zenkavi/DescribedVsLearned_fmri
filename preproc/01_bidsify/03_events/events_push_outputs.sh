#! /bin/bash

export OUT_PATH=/shared/bids_nifti_wface

aws s3 sync $OUT_PATH s3://described-vs-experienced/bids_nifti_wface
