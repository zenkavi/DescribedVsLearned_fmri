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
  export CODE_PATH=/shared/code/analysis/
  export BM_PATH=/shared/bids_nifti_wface/derivatives/fmriprep
  export BEHAVIOR_PATH=/shared/behavioral_data/

  if [[ ! -e $DATA_PATH ]]; then
    mkdir $DATA_PATH
    mkdir $DATA_PATH/level1
    mkdir $DATA_PATH/level2
    mkdir $DATA_PATH/level3
  fi

  if [[ ! -e $BEHAVIOR_PATH ]]; then
    mkdir $BEHAVIOR_PATH
  fi

  aws s3 sync s3://described-vs-experienced/code/analysis/ $CODE_PATH
  aws s3 cp s3://described-vs-experienced/behavioral_data/all_trials.csv $BEHAVIOR_PATH

  chown -R ec2-user: /shared
  chmod +x $CODE_PATH/01_level1/level1.py
  chmod +x $CODE_PATH/01_level1/run_level1.sh
  chmod +x $CODE_PATH/02_level2/level2.py
  chmod +x $CODE_PATH/02_level2/run_level2.sh
  chmod +x $CODE_PATH/03_level3/level3.py

  echo "alias squeue='squeue -o \"%.18i %.9P %.18j %.8u %.2t %.10M %.6D %R\"'">> /home/ec2-user/.bash_profile
fi
