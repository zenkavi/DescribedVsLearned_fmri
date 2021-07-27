#!/bin/bash

export DATA_PATH=/shared/bids_nifti_wface

ls -alt $DATA_PATH/sourcedata/bidsonym/sub-$1/images

ls $DATA_PATH/sourcedata/bidsonym/sub-$1/meta_data_info | wc

ls -alt $DATA_PATH/sub-$1/anat
ls -alt $DATA_PATH/sub-$1/fmap
ls -alt $DATA_PATH/sub-$1/func
