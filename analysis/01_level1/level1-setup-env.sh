#! /bin/bash
pip install --upgrade setuptools -U --user
pip install Cython -U --user
pip install nibabel -U --user
pip install nilearn -U --user
pip install numpy -U --user
pip install pandas -U --user

. "/etc/parallelcluster/cfnconfig"

if [[ "${cfn_node_type}" == "MasterServer" ]]
then
  mkdir /shared/.out
  mkdir /shared/.err

  export DATA_PATH=/shared/bids_nifti_wface
  export CODE_PATH=/shared/code/analysis/01_level1
  export OUT_PATH=/shared/bids_nifti_wface/derivatives/nilearn

  if [[ ! -e $DATA_PATH ]]; then
    mkdir $DATA_PATH
  fi

  aws s3 sync s3://described-vs-experienced/01_level1 $CODE_PATH

  if [[ ! -e $OUT_PATH ]]; then
    mkdir $OUT_PATH
  fi

  chown -R ec2-user: $DATA_PATH
  chown -R ec2-user: $CODE_PATH
  chown -R ec2-user: $OUT_PATH
  chown -R ec2-user: /shared/.out
  chown -R ec2-user: /shared/.err
  sudo chmod +x $CODE_PATH/level1.py

  echo "alias squeue='squeue -o \"%.18i %.9P %.18j %.8u %.2t %.10M %.6D %R\"'">> /home/ec2-user/.bash_profile
fi
