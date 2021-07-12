

Defacing anatomical images is a required step to share the data.
https://github.com/PeerHerholz/BIDSonym


## Run bidsonym on cluster

- Push code to s3 BUCKET
```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/home amazon/aws-cli s3 sync /home/02_deface s3://described-vs-experienced/02_deface --exclude ".DS_Store"
```

- Test on master node of cluster. Need to download data necessary for the job from s3 bucket
```
export DATA_PATH=/scratch/bids_nifti_wface
export CODE_PATH=/scratch/02_deface
export OUT_PATH=/scratch/bids_nifti_wface

if [[ ! -e $OUT_PATH ]]; then
  mkdir $OUT_PATH
fi

aws s3 sync s3://described-vs-experienced/raw_fmri_data/AR-GT-BUNDLES-01_RANGEL $DATA_PATH/AR-GT-BUNDLES-01_RANGEL

docker run --rm -it -v $DATA_PATH:/data \
-v $OUT_PATH:/out \
--cpus="4" --memory="8g" \
peerherholz/bidsonym:v0.0.4 \

```

- Submit bidsonym jobs. Make sure to make the shell script executable as pulling from S3 this is no longer set.
```
export CODE_PATH=/scratch/02_deface
cd $CODE_PATH
chmod +x run_bidsonym.sh
./run_bidsonym.sh
```
