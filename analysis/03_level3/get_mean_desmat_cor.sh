#!/bin/bash

export L1_PATH=/shared/bids_nifti_wface/derivatives/nilearn/glm/level1/
export L3_PATH=/shared/bids_nifti_wface/derivatives/nilearn/glm/level3/
export CODE_PATH=/shared/code/analysis/03_level3

for modelnum in 1
do
  for reg_rt in 0 1
  do
    aws s3 sync s3://described-vs-experienced/bids_nifti_wface/derivatives/nilearn/glm/level1/model$modelnum_reg-rt$reg_rt $DATA_PATH/model$modelnum_reg-rt$reg_rt

    docker run --rm -it \
    -v $L1_PATH:/data -v $L3_PATH:/out -v $CODE_PATH:/code \
    zenkavi/fsl:6.0.3 ./code/get_mean_desmat_cor.py --mnum $modelnum --reg_rt $reg_rt --l1_path /data --l3_path /out

    aws s3 sync $L3_PATH/model$modelnum_reg-rt$reg_rt s3://described-vs-experienced/bids_nifti_wface/derivatives/nilearn/glm/level3/$modelnum_reg-rt$reg_rt/
  done
done
