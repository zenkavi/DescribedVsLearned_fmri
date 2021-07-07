#! /bin/bash
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
chkconfig docker on
docker pull nipy/heudiconv:0.9.0

. "/etc/parallelcluster/cfnconfig"

if [[ "${cfn_node_type}" == "MasterServer" ]]
then
  mkdir /shared/.out
  mkdir /shared/.err
fi

export DATA_PATH=/shared/raw_fmri_data
export CODE_PATH=/shared/01_bidsify
export OUT_PATH=/shared/bids_nifti_wface

aws s3 sync s3://described-vs-experienced/01_bidsify $CODE_PATH

if [[ ! -e $OUT_PATH ]]; then
  mkdir $OUT_PATH
  aws s3 sync s3://described-vs-experienced/bids_nifti_wface $OUT_PATH
fi

if [[ ! -e $DATA_PATH ]]; then
  mkdir $DATA_PATH
fi

alias squeue='squeue -o "%.18i %.9P %.18j %.8u %.2t %.10M %.6D %R"'
