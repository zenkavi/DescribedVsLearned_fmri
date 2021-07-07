
######################################
# S3: Data storage
######################################

- Transfer data to S3
  - Single file
  ```
  export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
  docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR/00_aws:/home amazon/aws-cli s3 cp /home/test-setup-env.sh s3://described-vs-experienced/test-setup-env.sh
  ```

  - One subject folder  
  **Note: mounting the whole raw data folder uses a lot of CPU sp you should prob copy the directory you want to copy into a temporary empty dir first**
  ```
  export TMP_DIR=/Users/zeynepenkavi/Downloads/tmp
  mkdir TMP_DIR
  cp /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration/raw_fmri_data/AR-GT-BUNDLES-03_RANGEL $TMP_DIR/AR-GT-BUNDLES-03_RANGEL
  cd $TMP_DIR
  docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/aws amazon/aws-cli s3 sync /aws/AR-GT-BUNDLES-03_RANGEL s3://described-vs-experienced/raw_fmri_data/AR-GT-BUNDLES-03_RANGEL --exclude ".DS_Store"
  ```

- Check if transfer is successful. Trailing "/" matters for the content
```
aws s3 ls s3://described-vs-experienced/bids_nifti_wface/
```

######################################
# EC2: Single instance for testing
######################################

- Create key pair
```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
aws ec2 create-key-pair --key-name test-cluster --query 'KeyMaterial' --output text > $KEYS_PATH/test-cluster.pem
chmod 400 $KEYS_PATH/test-cluster.pem
```

- Create security group
```
export VPC_ID=`aws ec2 describe-vpcs | jq -j '.Vpcs[0].VpcId'`
aws ec2 create-security-group --group-name test-cluster-sg --description "test-cluster security group" --vpc-id $VPC_ID
```

- Allow SSH access to security group
```
export SG_ID=`aws ec2 describe-security-groups --filters Name=group-name,Values="test-cluster-sg"  | jq -j '.SecurityGroups[0].GroupId'`
export MY_IP=`curl ifconfig.me`
aws ec2 authorize-security-group-ingress \
   --group-id $SG_ID \
   --protocol tcp \
   --port 22 \
   --cidr $MY_IP/32
```

- Env set up to run instance (require `jq`)
```
export AMI_ID=ami-0b2ca94b5b49e0132
export KEY_NAME=test-cluster
export SG_ID=`aws ec2 describe-security-groups --filters Name=group-name,Values="test-cluster-sg"  | jq -j '.SecurityGroups[0].GroupId'`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
```

- Run instance
```
docker run --rm -it -v ~/.aws:/root/.aws amazon/aws-cli ec2 run-instances --image-id $AMI_ID --count 1 --instance-type t2.micro --key-name $KEY_NAME --security-group-ids $SG_ID --subnet-id $SUBNET_ID
```

- Run instance with user data
```
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/home amazon/aws-cli ec2 run-instances --image-id $AMI_ID --count 1 --instance-type t2.micro --key-name $KEY_NAME --security-group-ids $SG_ID --subnet-id $SUBNET_ID --user-data file:///home/test-setup-env.sh
```

- List running instances
```
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`]| [0].Value,InstanceType, PrivateIpAddress, PublicIpAddress]' --filters Name=instance-state-name,Values=running --output table
```

- Connect to running instance
```
export INSTANCE_IP=`aws ec2 describe-instances --filters Name=instance-state-name,Values=running | jq -j '.Reservations[0].Instances[0].PublicIpAddress'`
INSTANCE_IP=${INSTANCE_IP//./-}
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
ssh -i "$KEYS_PATH/test-cluster.pem" ec2-user@ec2-$INSTANCE_IP.us-west-1.compute.amazonaws.com
```

- Install docker on EC2 instance
```
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
```

- Log out+in and check if docker is working
```
docker info
```

- Download containers for e.g. heudiconv, mriqc, fmriprep onto EC2
```
docker pull nipy/heudiconv:0.9.0
```

- Give EC2 instance IAM role to access S3
```
export INSTANCE_ID=`aws ec2 describe-instances --filters Name=instance-state-name,Values=running | jq -j '.Reservations[0].Instances[0].InstanceId'`
aws ec2 associate-iam-instance-profile --instance-id $INSTANCE_ID --iam-instance-profile Name=S3FullAccessForEC2
```

- Copy content from S3 to EC2 instance after installing aws-cli
```
pip3 install awscli -U --user
aws s3 sync s3://described-vs-experienced/raw_fmri_data/AR-GT-BUNDLES-01_RANGEL ./AR-GT-BUNDLES-01_RANGEL
```

- Terminate instance
```
export INSTANCE_ID=`aws ec2 describe-instances --filters Name=instance-state-name,Values=running | jq -j '.Reservations[0].Instances[0].InstanceId'`
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
```

######################################
# AWS ParallelCluster
######################################

Use custom bootstrap actions to set up master and compute nodes

- Define env variables
```
export KEY_NAME=`aws ec2 describe-key-pairs | jq -j '.KeyPairs[0].KeyName'`
export SG_ID=`aws ec2 describe-security-groups --filters Name=group-name,Values="test-cluster"  | jq -j '.SecurityGroups[0].GroupId'`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
export VPC_ID=`aws ec2 describe-vpcs | jq -j '.Vpcs[0].VpcId'`
export REGION=`aws configure get region`
```

- Copy script with bootstrap actions to s3
```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc/00_aws
cd $STUDY_DIR
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/aws amazon/aws-cli s3 cp /aws/test-setup-env.sh s3://described-vs-experienced/test-setup-env.sh
```

- Set up temporary cluster config file with the environment variables piped in. Note the script below creates a `tmp.ini` file with the values piped in. Since I don't want to share these values publicly this file is not committed to my git history through a global setting in my `~/.gitignore` (ignores all files with `tmp` in the name).
```
./make_cluster_config_ini.sh
```

- Create cluster using temporary custom config.
```
pcluster create test-cluster -c tmp.ini
```

- Check cluster status
```
pcluster list --color
```

- Log onto cluster
```
pcluster ssh test-cluster -i $KEYS_PATH/test-cluster.pem
```

- Stop and start compute nodes of cluster
```
pcluster stop test-cluster

pcluster start test-cluster
```

- Update cluster
```
pcluster update test-cluster -c tmp.ini
```

- Check cluster resources
```
sinfo
```

- Change node status (see https://slurm.schedmd.com/scontrol.html for other state options)
```
scontrol: update NodeName={NODE_NAME} State=POWER_DOWN
```

- Delete cluster
```
pcluster delete test-cluster
```

######################################
# Lustre filesystem
######################################

- List contents of filesystem
```
ls -lh /lustre
```

- View how much data is stored
```
lfs df -h
```

- View state of file
```
lfs hsm_state /lustre/{FILENAME}
```

- Release file content
```
sudo lfs hsm_release /lustre/{FILENAME}
```

- Load content of a file
```
nohup find local/directory -type f -print0 | xargs -0 -n 1 sudo lfs hsm_restore &
```

- [Recommended though under development] To write data back to the S3 bucket
```
export FS_ID=`aws fsx describe-file-systems | jq -j '.FileSystems[0].FileSystemId'`
aws fsx create-data-repository-task \
    --file-system-id $FS_ID \
    --type EXPORT_TO_REPOSITORY \
    --paths /lustre/bids_nifti_wface \
    --report Enabled=false
```

- [Not recommended] Write single file back to s3
```
sudo lfs hsm_archive path/to/export/file
sudo lfs hsm_action path/to/export/file
```

- [Not recommended] Write directory back to s3
```
nohup find local/directory -type f -print0 | xargs -0 -n 1 sudo lfs hsm_archive &
```

- Check if export completed (since the task above runs in background)
```
find path/to/export/file -type f -print0 | xargs -0 -n 1 -P 8 sudo lfs hsm_action | grep "ARCHIVE" | wc -l
```

- To change data update policy (default with CLI is no update)
```
export FS_ID=`aws fsx describe-file-systems | jq -j '.FileSystems[0].FileSystemId'`
aws fsx update-file-system \
    --file-system-id $FS_ID \
    --lustre-configuration AutoImportPolicy=NEW_CHANGED
```
