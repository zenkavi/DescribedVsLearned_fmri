
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
# EC2: Computing
######################################
- EC2 and cluster specifications

--> Create template instance using Amazon Linux 2 AMI
--> Install software (heudiconv, bidsvalidator, defacing stuff, mriqc, fmriprep, study script repo - DescribedVsLearned_fmri)
--> Give access to S3 bucket
--> Save current state of instance as AMI
--> Keep this AMI as fmri-preproc
--> Data management:
  - Root is EBS.
  - Testing writes to this. When instance is destroyed testing output is destroyed too.
  - When running for all subjects read from and write to S3; with potential intermediate steps like Lustre SCRATCH


Env set up to run instance (require `jq`)
```
aws ec2 create-key-pair --key-name fmri-preproc --query 'KeyMaterial' --output text > fmri-preproc.pem
chmod 400 fmri-preproc.pem

aws ec2 create-security-group --group-name fmri-preproc-sg --description "fmri-preproc security group" --vpc-id [VPC-ID]

aws ec2 authorize-security-group-ingress \
   --group-name fmri-preproc-sg \
   --protocol tcp \
   --port 22 \
   --cidr [IP-ADDRESS]

export AMI_ID=ami-0b2ca94b5b49e0132
export KEY_NAME=`aws ec2 describe-key-pairs | jq -j '.KeyPairs[0].KeyName'`
export SG_ID=`aws ec2 describe-security-groups --filters Name=group-name,Values="fmri-preproc-sg"  | jq -j '.SecurityGroups[0].GroupId'`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
```

Run instance
```
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/aws amazon/aws-cli ec2 run-instances --image-id $AMI_ID --count 1 --instance-type t2.micro --key-name $KEY_NAME --security-group-ids $SG_ID --subnet-id $SUBNET_ID
```

List running instances
```
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`]| [0].Value,InstanceType, PrivateIpAddress, PublicIpAddress]' --filters Name=instance-state-name,Values=running --output table
```

- Test the following on single instance and run for all subjects on cluster
  - Heudiconv
  - Defacing
  - Mriqc
  - Fmriprep
