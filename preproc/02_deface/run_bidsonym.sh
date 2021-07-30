#!/bin/bash

export DATA_PATH=/shared/bids_nifti_wface

aws s3 sync s3://described-vs-experienced/bids_nifti_wface/sub-$1 $DATA_PATH/sub-$1

docker run \
-v $DATA_PATH:/data \
peerherholz/bidsonym:v0.0.4 \
/data \
participant \
--participant_label $1 \
--deid pydeface \
--brainextraction bet \
--bet_frac 0.5 \
--deface_t2w
