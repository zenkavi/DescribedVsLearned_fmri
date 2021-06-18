
######################################
# S3: Data storage
######################################
- Transfer data to S3
  - One subject
  ```
  aws s3 sync AR-GT-BUNDLES-02_RANGEL s3://described-vs-experienced/raw_fmri_data/AR-GT-BUNDLES-02_RANGEL --exclude ".DS_Store"
  ```
  - All data: [BEWARE, SHOULD TAKE VERY LONG!]
  ```
  aws s3 sync raw_fmri_data s3://described-vs-experienced/raw_fmri_data --exclude ".DS_Store"
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
--> Create template instance using Amazon Linux 2 AMI
--> Install software (heudiconv, mriqc, fmriprep)
  - This could all possibly be done by specifying in `user data` option when running the instance
--> Give access to S3 bucket through IAM role for testing *only*
  - **This won't be enough to run anything on S3 content. Content would have to be downloaded to the instance to actually do anything with them**
--> Save current state of instance as AMI
--> Keep this AMI as fmri-preproc
--> Data management:
  - Root is EBS. *Do you need/want automated snapshots?*
  - When running for all subjects read from and write to S3; with potential intermediate steps like Lustre SCRATCH


- Key pair and security group creation to connect to the instance
```
aws ec2 create-key-pair --key-name fmri-preproc --query 'KeyMaterial' --output text > fmri-preproc.pem
chmod 400 fmri-preproc.pem

aws ec2 create-security-group --group-name fmri-preproc-sg --description "fmri-preproc security group" --vpc-id [VPC-ID]

aws ec2 authorize-security-group-ingress \
   --group-name fmri-preproc-sg \
   --protocol tcp \
   --port 22 \
   --cidr [IP-ADDRESS]
```

- Env set up to run instance (require `jq`)
```
export AMI_ID=ami-0b2ca94b5b49e0132
export KEY_NAME=`aws ec2 describe-key-pairs | jq -j '.KeyPairs[0].KeyName'`
export SG_ID=`aws ec2 describe-security-groups --filters Name=group-name,Values="fmri-preproc-sg"  | jq -j '.SecurityGroups[0].GroupId'`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
```

- Run instance
```
docker run --rm -it -v ~/.aws:/root/.aws amazon/aws-cli ec2 run-instances --image-id $AMI_ID --count 1 --instance-type t2.micro --key-name $KEY_NAME --security-group-ids $SG_ID --subnet-id $SUBNET_ID
```

- List running instances
```
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`]| [0].Value,InstanceType, PrivateIpAddress, PublicIpAddress]' --filters Name=instance-state-name,Values=running --output table
```

- Connect to running instance
```
ssh -i "fmri-preproc.pem" ec2-user@[IP-ADDRESS].us-west-1.compute.amazonaws.com
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

- Download containers for heudiconv, mriqc, fmriprep,
```
docker pull nipy/heudiconv:latest
docker pull poldracklab/mriqc:latest
docker pull poldracklab/fmriprep:latest
```

[For single instance testing]
- Give EC2 instance IAM role to access S3
```
aws ec2 associate-iam-instance-profile --instance-id [INSTANCE_ID] --iam-instance-profile Name=S3FullAccessForEC2
```

- Copy content from S3
```
aws s3 sync s3://[BUCKET-NAME]/AR-GT-BUNDLES-01_RANGEL ./AR-GT-BUNDLES-01_RANGEL
```

######################################
# AWS ParallelCluster
######################################

- Use custom bootstrap actions to set up master and compute nodes
```
export KEY_NAME=`aws ec2 describe-key-pairs | jq -j '.KeyPairs[0].KeyName'`
export SG_ID=`aws ec2 describe-security-groups --filters Name=group-name,Values="fmri-preproc-sg"  | jq -j '.SecurityGroups[0].GroupId'`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
export VPC_ID=`aws ec2 describe-vpcs | jq -j '.Vpcs[0].VpcId'`
export REGION=`aws configure get region`
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc

aws s3 cp $STUDY_DIR/00_aws/setup_cluster_env.sh s3://described-vs-experienced/setup_cluster_env.sh

pcluster create fmri-preproc-cluster -c fmri-preproc-cluster.ini

pcluster list --color

pcluster ssh [NAME OF CLUSTER] -i [KEY FILE PATH]
```

- Delete cluster
```
pcluster delete fmri-preproc
```
