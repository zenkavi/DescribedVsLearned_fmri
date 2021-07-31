
## Push code to s3 bucket
```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/home amazon/aws-cli s3 sync /home/03_fmriprep s3://described-vs-experienced/03_fmriprep
```

## Make cluster
```
./fmriprep_cluster_config_ini.sh
pcluster create test-cluster -c tmp.ini
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
pcluster ssh test-cluster -i $KEYS_PATH/test-cluster.pem
```

What kind of instance do you need for the compute fleet?  
- 8GB memory per subject
- 8-16 CPUs per subject
- Note on AWS s vCPU are CPU x 2 because each CPU allows hyper-threading
- Note also that you need to make that your root volumes are big enough for the fmriprep docker image (as specified with the `master_root_volume_size` and `compute_root_volume_size` in the cluster configuration; these arguments are not listed in the AWS ParallelCluster documentation)

## fmriprep command template
```
export DATA_PATH=/shared/bids_nifti_wface
export TMP_PATH=/shared/tmp
export FS_LICENSE=/shared/license.txt

aws s3 sync s3://described-vs-experienced/bids_nifti_wface/sub-01 $DATA_PATH/sub-01

docker run -ti --rm  \
-v $DATA_PATH:/data:ro  \
-v $DATA_PATH/derivatives:/out  \
-v $TMP_DIR:/work  \
-v $FS_LICENSE:/opt/freesurfer/license.txt  \
-m=16g  \
--cpus="12"  \
nipreps/fmriprep:20.2.3  \
/data /out participant  \
--participant-label 01 \
-w /work --skip_bids_validation --output-spaces MNI152NLin2009cAsym:res-2 --fs-no-reconall
```

To get subject freesurfer segmentation remove
```
--fs-no-reconall
```
but note that this will take at least 20hrs per subject.

What outputs need to be pushed back to s3?
