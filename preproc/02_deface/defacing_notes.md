

Defacing anatomical images is a required step to share the data. I use the BIDS app [`BIDSonym`](https://github.com/PeerHerholz/BIDSonym) to do this.   

Initially I used parallel jobs on a cluster to do this but there were some errors that were difficult to debug and fix. The outputs of this operation are written into the BIDS directory so if something breaks and you don't notice when it does you need to do lots of manual checks through each subject's files. So now I prefer running it for each subject individually and examining the output before writing back to S3.

## Run bidsonym on EC2

- Push code to s3 BUCKET **why does this hang sometimes?!**
```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/home amazon/aws-cli s3 sync /home/02_deface s3://described-vs-experienced/02_deface
```

- Test on single subject Need to download data necessary for the job from s3 bucket
```
export DATA_PATH=/scratch/bids_nifti_wface
export CODE_PATH=/scratch/02_deface

aws s3 sync s3://described-vs-experienced/02_deface $CODE_PATH
aws s3 sync s3://described-vs-experienced//bids_nifti_wface/sub-01 $DATA_PATH/sub-01

docker run --rm -it -v $DATA_PATH:/data \
peerherholz/bidsonym:v0.0.4 \
/data \
participant \
--participant_label 01 \
--deid pydeface \
--brain_extraction bet \
--bet_frac 0.5 \
--deface_t2w
```

- Once testing is done you can either submit each subject to run parallel
```
cd $CODE_PATH
chmod +x run_bidsonym.sh
./run_bidsonym.sh
```

- Or you can run the jobs as a loop. This would be much slower but when run in parallel some jobs can error out due to changes in the BIDS layout of the root directory from other jobs finishing and cleaning up before a job is done.
```
cd $CODE_PATH
sbatch run_bidsonym_loop.batch
```
