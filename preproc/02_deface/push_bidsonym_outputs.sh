#!/bin/bash

aws s3 sync $DATA_PATH/sub-$1 s3://described-vs-experienced/bids_nifti_wface/sub-$1
aws s3 sync $DATA_PATH/sourcedata/bidsonym s3://described-vs-experienced/bids_nifti_wface/sourcedata/bidsonym
sudo chown -R ec2-user: $DATA_PATH/sub-$1
sudo chown -R ec2-user: $DATA_PATH/sourcedata/bidsonym
rm -rf $DATA_PATH/sub-$1
rm -rf $DATA_PATH/sourcedata/bidsonym/sub-$1
