================================================================================  
Heudiconv
================================================================================  

[Heudiconv](https://heudiconv.readthedocs.io/en/latest/) converts DICOMs to Nifti in BIDS format.

## Make heuristics file

**IMPORTANT**: If you're using zsh, which is the new default on Mac Terminals you need to include `noglob` before running the docker image so it interprets the `*` wildcards correctly.

- Explore DICOM structures and specify the `heuristics` file.
```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/tmp:/base nipy/heudiconv:latest \
-d /base/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-o /base/ \
-f convertall \
-s 03 \
-c none --overwrite
```

- Get all subjects' ages from dicoms
```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration:/base nipy/heudiconv:latest \
-d /base/raw_fMRI_data/AR-GT-BUNDLES-{subject}_RANGEL/*/LOCALIZER_*/*.IMA \
-o /base/Nifti/ \
-f convertall \
-s 02 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 27 \
-c none --overwrite
```

- Convert dicoms of subject 01 into BIDS locally after copying single subject directory out to a temporary directory to avoid mounting the whole raw data directory. Check this then with the bidsvalidator on a browser to make sure the heuristics file is correct
```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/tmp:/base  \
-v /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration/bids_nifti_wface:/out \
-v /Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc/01_bidsify:/code \
nipy/heudiconv:latest \
-d /base/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-b -o /out/ \
-f /code/heuristic.py \
-s 01 \
-c dcm2niix --overwrite
```

## Run heudiconv on cluster

- Push code to s3 BUCKET
```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/home amazon/aws-cli s3 sync /home/01_bidsify s3://described-vs-experienced/01_bidsify --exclude ".DS_Store"
```

- Test on master node of cluster. Need to download data necessary for the job from s3 bucket
```
export DATA_PATH=/scratch/raw_fmri_data
export CODE_PATH=/scratch/01_bidsify
export OUT_PATH=/scratch/bids_nifti_wface

if [[ ! -e $OUT_PATH ]]; then
  mkdir $OUT_PATH
  aws s3 sync s3://described-vs-experienced/bids_nifti_wface $OUT_PATH
fi

aws s3 sync s3://described-vs-experienced/raw_fmri_data/AR-GT-BUNDLES-01_RANGEL $DATA_PATH/AR-GT-BUNDLES-01_RANGEL

docker run --rm -it -v $DATA_PATH:/data \
-v $OUT_PATH:/out \
--cpus="4" --memory="8g" \
nipy/heudiconv:0.9.0 \
-d /data/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-b -o /out/ \
-f convertall \
-s 01 \
-c none --overwrite

docker run --rm -it -v $DATA_PATH:/data \
-v $OUT_PATH:/out \
-v $CODE_PATH:/code \
--cpus="4" --memory="8g" \
nipy/heudiconv:0.9.0 \
-d /data/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-b -o /out/ \
-f /code/heuristic.py \
-s 01 \
-c dcm2niix --overwrite
```

- To debug heudiconv docker container on master node: override entrypoint executable and run shell in the container
```
docker run --rm -it --cpus="4" --memory="8g" -v $DATA_PATH:/data -v $OUT_PATH:/out --entrypoint /bin/bash nipy/heudiconv:0.9.0
```

- Submit heudiconv jobs. Make sure to make the shell script executable as pulling from S3 this is no longer set.
```
export CODE_PATH=/scratch/01_bidsify
cd $CODE_PATH
chmod +x run_heudiconv.sh
./run_heudiconv.sh
```

- Subject 02's data was collected on two days so their DICOMs have differing `StudyUIDs`. This breaks `heudiconv`. To
(see here for discussions of the [problem](https://neurostars.org/t/conflicting-study-identifiers/4729/5) and a [solution](https://github.com/nipy/heudiconv/issues/280))
```
sbatch run_heudiconv_sub02.batch
```

================================================================================  
Physio
================================================================================  

### What do we have and how do we get it to be bids compatible?

We have raw Siemens PMU data for pulse, respiration, ecg, and external trigger pulses
They are sampled at different frequencies ().ecg 100 Hz, .puls 50 Hz, .resp 50 Hz, .ext 100 Hz). According to [BIDS specification](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/06-physiological-and-other-continuous-recordings.html) "recordings with different sampling frequencies and/or starting times should be stored in separate files.""

### Does fmriprep use physio data?

No, instead they use CompCor to derive confound regressors. See [this](https://neurostars.org/t/physiological-data-in-fmriprep/2846) and [this](https://neurostars.org/t/combining-physio-and-fmriprep/17891) thread.

Raw physio data can be turned into confound regressors by resampling and aligning using other software (e.g. the SPM plug-in physIO) **BUT** the fmriprep CompCor components capture the same nuisance regressors I'll include the physio data with minimal processing for the sake of completeness in the BIDS dataset but not use them in the GLMs.

The output should look like:
```
sub-<label>/
  func/
      sub-<label>_task-bundles_run-1_recording-breathing_physio.tsv.gz
      sub-<label>_task-bundles_run-1_recording-breathing_physio.json
      sub-<label>_task-bundles_run-1_recording-cardiac_physio.tsv.gz
      sub-<label>_task-bundles_run-1_recording-cardiac_physio.json
```
where the TSV files specified do not include a header line. Instead the name of columns are specified in the JSON file.

## Run preprocessing script on EC2

- Env set up to run instance
```
export AMI_ID=ami-0b2ca94b5b49e0132
export KEY_NAME=test-cluster
export SG_ID=`aws ec2 describe-security-groups --filters Name=group-name,Values="test-cluster-sg"  | jq -j '.SecurityGroups[0].GroupId'`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
```

- Run instance
```
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/home amazon/aws-cli ec2 run-instances --image-id $AMI_ID --count 1 --instance-type t2.xlarge --key-name $KEY_NAME --security-group-ids $SG_ID --subnet-id $SUBNET_ID
```

- Push code to s3 BUCKET
```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/home amazon/aws-cli s3 sync /home/01_bidsify s3://described-vs-experienced/01_bidsify --exclude ".DS_Store"
```

- Connect to running instance
```
export INSTANCE_IP=`aws ec2 describe-instances --filters Name=instance-state-name,Values=running | jq -j '.Reservations[0].Instances[0].PublicIpAddress'`
INSTANCE_IP=${INSTANCE_IP//./-}
ssh -i "$KEYS_PATH/test-cluster.pem" ec2-user@ec2-$INSTANCE_IP.us-west-1.compute.amazonaws.com
```

- Give EC2 instance IAM role to access S3
```
export INSTANCE_ID=`aws ec2 describe-instances --filters Name=instance-state-name,Values=running | jq -j '.Reservations[0].Instances[0].InstanceId'`
aws ec2 associate-iam-instance-profile --instance-id $INSTANCE_ID --iam-instance-profile Name=S3FullAccessForEC2
```

- Copy content from S3 to EC2 instance
```
chmod +x physio-setup-env.sh
./physio-setup-env.sh
```

- Terminate instance
```
export INSTANCE_ID=`aws ec2 describe-instances --filters Name=instance-state-name,Values=running | jq -j '.Reservations[0].Instances[0].InstanceId'`
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
```

================================================================================
Event files
================================================================================

Files describing what happened in each bold run with the name format:
```
sub-<label>_task-bundles_run-<label>_events.tsv
```

and columns
```
onset
duration
trial_type
response_time
```

In .mat behavioral data files there are

```
onsetCross
onsetProbabilities
onsetStimulus
onsetReward
```

================================================================================
Double check sidecars (e.g. for fieldmaps)
================================================================================

================================================================================
bidsvalidator
================================================================================

Already ran once as part of defacing.
