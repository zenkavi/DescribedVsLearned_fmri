

Defacing anatomical images is a required step to share the data. I use the BIDS app [`BIDSonym`](https://github.com/PeerHerholz/BIDSonym) to do this.   

Initially I used parallel jobs on a cluster to do this but there were some errors that were difficult to debug and fix. The outputs of this operation are written into the BIDS directory so if something breaks and you don't notice when it does you need to do lots of manual checks through each subject's files. So now I prefer running it for each subject individually and examining the output before writing back to S3.

## Run bidsonym on EC2

- Push code to s3 BUCKET **why does this hang sometimes?!**
```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/home amazon/aws-cli s3 sync /home/02_deface s3://described-vs-experienced/02_deface --exclude ".DS_Store"
```

- Test on single subject Need to download data necessary for the job from s3 bucket
```
export DATA_PATH=/scratch/bids_nifti_wface
export CODE_PATH=/scratch/02_deface

if [[ ! -e $DATA_PATH ]]; then
  mkdir $DATA_PATH
fi

aws s3 sync s3://described-vs-experienced//bids_nifti_wface/sub-01 $DATA_PATH/sub-01

docker run --rm -it -v $DATA_PATH:/data \
peerherholz/bidsonym:v0.0.4 \
/data \
participant \
--participant_label 01 \
--deid pydeface \
--brain_extraction bet \
--bet_frac 0.5 \
--del_meta 'InstitutionAddress'
--deface_t2w
```
- Check outputs  
  - Do the following exist in `sourcedata/bidsonym/sub-{SUBNUM}/images`
  ```
  sub-{SUBNUM}_T1w_brainmask_desc-nondeid.nii.gz  
  sub-{SUBNUM}_T1w_desc-nondeid.nii.gz  
  sub-{SUBNUM}_T2w_brainmask_desc-nondeid.nii.gz  
  sub-{SUBNUM}_T2w_desc-nondeid.nii.gz
  ```
  - What is in `sourcedata/bidsonym/sub-{SUBNUM}/meta_data_info`?
  ```
  ls -alt $DATA_PATH/sourcedata/bidsonym/sub-{SUBNUM}/meta_data_info
  ```
  - When are the anatomicals and sidecars in all image directories in `$DATA_PATH` last changed?
  ```
  ls -alt $DATA_PATH/sub-{SUBNUM}/anat
  ls -alt $DATA_PATH/sub-{SUBNUM}/fmap
  ls -alt $DATA_PATH/sub-{SUBNUM}/func
  ```

- Push to S3 when all is ready
