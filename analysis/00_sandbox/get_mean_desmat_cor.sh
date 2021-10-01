#!/bin/bash

export L1_PATH=/shared/bids_nifti_wface/derivatives/nilearn/glm/level1/
export L2_PATH=/shared/bids_nifti_wface/derivatives/nilearn/glm/level2/

for modelnum in 3 4 5 6 7
do
  for reg_rt in 0
  do
    aws s3 sync s3://described-vs-experienced/bids_nifti_wface/derivatives/nilearn/glm/level1/model$modelnum_reg-rt$reg_rt $DATA_PATH/model$modelnum_reg-rt$reg_rt

    docker run --rm -it \
    -v $L1_PATH:/data -v $L2_PATH:/out
    zenkavi/fsl:6.0.3 ./code/get_mean_desmat_cor.py --mnum $modelnum --reg_rt $reg_rt --l1_path /data --l3_path /out

    aws s3 sync $L2_PATH/model$modelnum_reg-rt$reg_rt s3://described-vs-experienced/bids_nifti_wface/derivatives/nilearn/glm/level2/$modelnum_reg-rt$reg_rt/
  done
done
