#!/bin/bash

export DATA_PATH=/shared/bids_nifti_wface

aws s3 sync s3://described-vs-experienced/bids_nifti_wface/sub-$1 $DATA_PATH/sub-$1

docker run -ti --rm -v $DATA_PATH:/data:ro bids/validator:v1.8.1-dev.0 /data

rm -rf $DATA_PATH/sub-$1
