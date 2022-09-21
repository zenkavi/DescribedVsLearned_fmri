#! /bin/bash
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
chkconfig docker on
docker pull zenkavi/fsl:6.0.3

. "/etc/parallelcluster/cfnconfig"

if [[ "${cfn_node_type}" == "MasterServer" ]]
then
  mkdir /shared/.out
  mkdir /shared/.err

  export DATA_PATH=/shared/bids_nifti_wface/derivatives/nilearn/glm
  export CODE_PATH=/shared/analysis/
  export BM_PATH=/shared/bids_nifti_wface/derivatives/fmriprep
  export BEHAVIOR_PATH=/shared/behavioral_data/

  if [[ ! -e $DATA_PATH ]]; then
    mkdir $DATA_PATH
    mkdir $DATA_PATH/level1
    mkdir $DATA_PATH/level2
  fi

  if [[ ! -e $BEHAVIOR_PATH ]]; then
    mkdir $BEHAVIOR_PATH
  fi

  aws s3 cp s3://described-vs-experienced/behavioral_data/all_trials.csv $BEHAVIOR_PATH

  chown -R ec2-user: /shared

  echo "alias squeue='squeue -o \"%.18i %.9P %.18j %.8u %.2t %.10M %.6D %R\"'">> /home/ec2-user/.bash_profile
fi
