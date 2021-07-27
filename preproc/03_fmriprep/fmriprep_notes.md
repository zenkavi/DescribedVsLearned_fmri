
Command template

```
export DATA_PATH=/shared/bids_nifti_wface
export TMP_PATH=/shared/tmp
export FS_LICENSE=/shared/license.txt

docker run -ti --rm  \
-v $DATA_PATH:/data:ro  \
-v $DATA_PATH:/out  \
-v $TMP_DIR:/work  \
-v $FS_LICENSE:/opt/freesurfer/license.txt  \
nipreps/fmriprep:20.2.3  \
data out participant  \
-w work --skip_bids_validation --md-only-boilerplate --output-layout bids
```
