#! /bin/zsh

export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/base amazon/aws-cli s3 sync /base/01_bidsify s3://described-vs-experienced/01_bidsify --exclude ".DS_Store"
