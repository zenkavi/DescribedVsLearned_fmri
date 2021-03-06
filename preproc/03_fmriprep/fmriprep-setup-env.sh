#! /bin/bash
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
chkconfig docker on
docker pull nipreps/fmriprep:20.2.3

. "/etc/parallelcluster/cfnconfig"

if [[ "${cfn_node_type}" == "MasterServer" ]]
then
  mkdir /shared/.out
  mkdir /shared/.err

  export DATA_PATH=/shared/bids_nifti_wface
  export CODE_PATH=/shared/code/preproc/03_fmriprep
  export TMP_PATH=/shared/tmp

  aws s3 sync s3://described-vs-experienced/code/preproc/03_fmriprep $CODE_PATH
  aws s3 cp s3://described-vs-experienced/license.txt /shared/license.txt

  if [[ ! -e $TMP_PATH ]]; then
    mkdir $TMP_PATH
  fi

  if [[ ! -e $DATA_PATH ]]; then
    mkdir $DATA_PATH
    aws s3 cp s3://described-vs-experienced/bids_nifti_wface/dataset_description.json $DATA_PATH/dataset_description.json
    aws s3 cp s3://described-vs-experienced/bids_nifti_wface/participants.json $DATA_PATH/participants.json
    aws s3 cp s3://described-vs-experienced/bids_nifti_wface/participants.tsv $DATA_PATH/participants.tsv
    aws s3 cp s3://described-vs-experienced/bids_nifti_wface/task-bundles_bold.json $DATA_PATH/task-bundles_bold.json
    aws s3 cp s3://described-vs-experienced/bids_nifti_wface/CHANGES $DATA_PATH/CHANGES
    aws s3 cp s3://described-vs-experienced/bids_nifti_wface/README $DATA_PATH/README
    aws s3 sync s3://described-vs-experienced/bids_nifti_wface/stimuli $DATA_PATH/stimuli
  fi

  chown -R ec2-user: $DATA_PATH
  chown -R ec2-user: $CODE_PATH
  chown -R ec2-user: $TMP_PATH
  chown -R ec2-user: /shared/.out
  chown -R ec2-user: /shared/.err

  echo "alias squeue='squeue -o \"%.18i %.9P %.18j %.8u %.2t %.10M %.6D %R\"'">> /home/ec2-user/.bash_profile
fi
