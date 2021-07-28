
Command template

```
export DATA_PATH=/shared/bids_nifti_wface
export TMP_PATH=/shared/tmp
export FS_LICENSE=/shared/license.txt

aws s3 sync s3://described-vs-experienced/bids_nifti_wface/sub-01 $DATA_PATH/sub-01

docker run -ti --rm  \
-v $DATA_PATH:/data:ro  \
-v $DATA_PATH:/out  \
-v $TMP_DIR:/work  \
-v $FS_LICENSE:/opt/freesurfer/license.txt  \
-m=16g  \
--cpus="12"  \
nipreps/fmriprep:20.2.3  \
/data /out participant  \
--participant-label 01 \
-w /work --skip_bids_validation --md-only-boilerplate --output-layout bids
```

What kind of instance do you need?
8GB memory per subject
8-16 CPUs per subject
