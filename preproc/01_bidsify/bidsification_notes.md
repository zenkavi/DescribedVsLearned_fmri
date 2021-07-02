
######################################
# Heudiconv
######################################  
Convert DICOMs to Nifti in BIDS format  

**IMPORTANT**: If you're using zsh, which is the new default on Mac Terminals you need to include `noglob` before running the docker image so it interprets the `*` wildcards correctly.

- Explore DICOM structures and specify the `heuristics` file.
```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration:/base nipy/heudiconv:latest \
-d /base/raw_fMRI_data/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
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

- How to run heudiconv parallel on cluster?
  - Push code to s3 BUCKET
  ```
  export $STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
  docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/home amazon/aws-cli s3 sync /home/01_bidsify s3://described-vs-experienced/01_bidsify --exclude ".DS_Store"
  ```
  - Submit heudiconv jobs
  ```
  /lustre/01_bidsify/run_heudiconv,sh
  ```
  - Test on master node
  ```
  docker run --rm -it -v $DATA_PATH:/data \
  -v $OUT_PATH:/out \
  -v $CODE_PATH:/code \
  nipy/heudiconv:0.9.0 \
  -d /data/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
  -b -o /out/ \
  -f /code/heuristic.py \
  -s 01 \
  -c dcm2niix --overwrite
  ```
  - Export data to s3 bucket
  ```
  ```
  - Delete cluster
  ```
  ```

######################################
# Physio
######################################

######################################
# Event files
######################################

######################################
# bidsvalidator
######################################
