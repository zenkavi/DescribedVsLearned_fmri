#! /bin/zsh

export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR/00_aws:/home amazon/aws-cli s3 cp /home/test-setup-env.sh s3://described-vs-experienced/test-setup-env.sh
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/home amazon/aws-cli s3 sync /home/01_bidsify s3://described-vs-experienced/01_bidsify --exclude ".DS_Store"
