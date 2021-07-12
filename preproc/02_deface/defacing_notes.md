

Defacing anatomical images is a required step to share the data. I use the BIDS app [`BIDSonym`](https://github.com/PeerHerholz/BIDSonym) to do this

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

aws s3 sync s3://described-vs-experienced//bids_nifti_wface/sub-01 $DATA_PATH/sub-01

docker run --rm -it -v $DATA_PATH:/data \
-v $OUT_PATH:/out \
--cpus="4" --memory="8g" \
peerherholz/bidsonym:v0.0.4 \
/data \
participant \
--participant_label 01 \
--deid pydeface \
--brain_extraction bet \
--bet_frac 0.5 \
--del_meta 'InstitutionAddress' \

```

- Submit bidsonym jobs. Make sure to make the shell script executable as pulling from S3 this is no longer set.
```
export CODE_PATH=/scratch/02_deface
cd $CODE_PATH
chmod +x run_bidsonym.sh
./run_bidsonym.sh
```
