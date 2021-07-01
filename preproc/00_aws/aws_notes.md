
######################################
# S3: Data storage
######################################

- Transfer data to S3
  - Single file
  ```
  export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc/00_aws
  cd $STUDY_DIR
  docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/aws amazon/aws-cli s3 cp /aws/test-setup-env.sh s3://described-vs-experienced/test-setup-env.sh
  ```

  - One subject folder  
  **note: mounting the whole raw data folder uses a lot of CPU**
  ```
  docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/aws amazon/aws-cli s3 sync /aws/AR-GT-BUNDLES-03_RANGEL s3://described-vs-experienced/raw_fmri_data/AR-GT-BUNDLES-03_RANGEL --exclude ".DS_Store"
  ```

  - Template BIDS folder
  ```
  aws s3 sync bids_nifti_wface s3://described-vs-experienced/bids_nifti_wface --exclude ".DS_Store"
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
aws ec2 authorize-security-group-ingress \
   --group-name test-cluster-sg \
   --protocol tcp \
   --port 22
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
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc/00_aws
docker run --rm -it -v ~/.aws:/root/.aws -v $STUDY_DIR:/base amazon/aws-cli ec2 run-instances --image-id $AMI_ID --count 1 --instance-type t2.micro --key-name $KEY_NAME --security-group-ids $SG_ID --subnet-id $SUBNET_ID --user-data /base/test-setup-env.sh
```

- List running instances
```
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`]| [0].Value,InstanceType, PrivateIpAddress, PublicIpAddress]' --filters Name=instance-state-name,Values=running --output table
```

- Connect to running instance
```
ssh -i "test-cluster.pem" ec2-user@ec2-[IP-ADDRESS].us-west-1.compute.amazonaws.com
```

- Install docker on EC2 instance
```
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```

- Log out+in and check if docker is working
```
docker info
```

- Download containers for e.g. heudiconv, mriqc, fmriprep,
```
docker pull nipy/heudiconv:0.9.0
```

- Give EC2 instance IAM role to access S3
```
aws ec2 associate-iam-instance-profile --instance-id [INSTANCE_ID] --iam-instance-profile Name=S3FullAccessForEC2
```

- Copy content from S3 to EC2 instance
```
aws s3 sync s3://[BUCKET-NAME]/AR-GT-BUNDLES-01_RANGEL ./AR-GT-BUNDLES-01_RANGEL
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
- Set up temporary cluster config file with the environment variables piped in
```
cat > tmp.ini << EOF
[aws]
aws_region_name = ${REGION}

[global]
cluster_template = default
update_check = false
sanity_check = true

[cluster default]
key_name = test-cluster
vpc_settings = public
base_os = alinux2
ebs_settings = myebs
fsx_settings = myfsx
master_instance_type = t2.micro
placement_group = DYNAMIC
placement = compute
disable_hyperthreading = true
scheduler = slurm
s3_read_write_resource = arn:aws:s3:::described-vs-experienced*
post_install = s3://described-vs-experienced/test-setup-env.sh

[compute_resource default]
instance_type = t2.micro
min_count = 0
max_count = 4

[vpc public]
vpc_id = ${VPC_ID}
master_subnet_id = ${SUBNET_ID}

[ebs myebs]
shared_dir = /shared
volume_type = gp2
volume_size = 50

[fsx myfsx]
shared_dir = /lustre
storage_capacity = 1200
import_path =  s3://described-vs-experienced
deployment_type = SCRATCH_2

[aliases]
ssh = ssh {CFN_USER}@{MASTER_IP} {ARGS}
EOF
```
- Create cluster using temporary custom config
```
pcluster create test-cluster -c tmp.ini

pcluster list --color

pcluster ssh test-cluster -i [KEY FILE PATH]
```

- Delete cluster
```
pcluster delete test-cluster
```
