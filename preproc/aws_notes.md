
######################################
# AWS CLI
######################################
Update the local image to the latest

```
docker pull amazon/aws-cli:latest
```

Run aws cli giving it access to user configuration

```
docker run --rm -it -v ~/.aws:/root/.aws amazon/aws-cli
```

------------------------------------------------------------------------------------------

Notes below based on this tutorial: https://www.hpcworkshops.com/

######################################
# Cloud9 environment
######################################

- If not using local terminal for command line use AWS Management Console > Cloud9 to create environment.

- Install/update AWS CLI
```
pip3 install awscli -U --user
```
######################################
# S3
######################################
[In cloud9 environment]

- Create S3 bucket
```
BUCKET_POSTFIX=$(uuidgen --random | cut -d'-' -f1)
aws s3 mb s3://bucket-${BUCKET_POSTFIX}
```

- Upload file to s3 bucket
```
aws s3 cp ./SEG_C3NA_Velocity.sgy s3://bucket-${BUCKET_POSTFIX}/SEG_C3NA_Velocity.sgy
```

- Check bucket contents
```
aws s3 ls s3://bucket-${BUCKET_POSTFIX}/
```
######################################
# EC2
######################################
[In cloud9 environment]

- Generate a key pair for SSH access into the EC2 instance
```
aws ec2 create-key-pair --key-name lab-2-your-key --query KeyMaterial --output text > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
```

- Identify the Subnet ID and VPC (virtual private cloud) ID of the cloud9 instance
```
MAC=$(curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/)
cat << EOF
***********************************************************************************
Subnet ID = $(curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/$MAC/subnet-id)
VPC ID = $(curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/$MAC/vpc-id)
************************************************************************************
EOF
```

- List information on instances
```
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`]| [0].Value,InstanceType, PrivateIpAddress, PublicIpAddress]' --filters Name=instance-state-name,Values=running --output table
```

- To give EC2 access to S3
  - create an IAM role with `AmazonS3FullAccess` policy
  - then in EC2 > Instances > select instance > Actions > Security > Modify IAM role

######################################
# Parallel Cluster
######################################
[In cloud9 environment]

- Install Parallel
```
pip3 install aws-parallelcluster -U --user
```

- Make template cluste config file
```
cat > ~/.parallelcluster/config << EOF
[aws]
aws_region_name = ${REGION}

[cluster default]
key_name = lab-3-your-key
vpc_settings = public
base_os = alinux2
scheduler = slurm

[vpc public]
vpc_id = ${VPC_ID}
master_subnet_id = ${SUBNET_ID}

[global]
cluster_template = default
update_check = false
sanity_check = true

[aliases]
ssh = ssh {CFN_USER}@{MASTER_IP} {ARGS}
EOF
```

- Make custom cluster config
```
cat > my-cluster-config.ini << EOF
> [aws]
> aws_region_name = ${REGION}
>
> [global]
> cluster_template = default
> update_check = false
> sanity_check = true
>
> [vpc public]
> vpc_id = ${VPC_ID}
> master_subnet_id = ${SUBNET_ID}
>
> [cluster default]
> key_name = lab-3-your-key
> base_os = alinux2
> scheduler = slurm
> master_instance_type = c5.xlarge
> s3_read_write_resource = *
> vpc_settings = public
> ebs_settings = myebs
> queue_settings = compute
>
> [queue compute]
> compute_resource_settings = default
> disable_hyperthreading = true
> placement_group = DYNAMIC
>
> [compute_resource default]
> instance_type = c5.large
> min_count = 0
> max_count = 8
>
> [ebs myebs]
> shared_dir = /shared
> volume_type = gp2
> volume_size = 20
>
> [aliases]
> ssh = ssh {CFN_USER}@{MASTER_IP} {ARGS}
> EOF
```

- Create cluster with custom config
```
pcluster create hpclab-yourname -c my-cluster-config.ini
```

- Connect to your cluster
```
pcluster ssh hpclab-yourname -i ~/.ssh/lab-3-key
```

- View and load modules in your cluster
```
module av
module load intelmpi
```

- List shared volumes between login/head and compute nodes
```
showmount -e localhost
```

- Update configurations of your cluster by
```
pcluster stop hpclab-yourname
vi my-cluster-config.ini
pcluster update hpclab-yourname -c my-cluster-config.ini
pcluster start hpclab-yourname
```

- Terminate cluster
```
pcluster delete hpclab-yourname
```
######################################
# FSx for Lustre
######################################
[In cloud9 environment]

- Lustre allows you to link an S3 bucket to your cluster without overloading your cluster immediately by loading all the data from the bucket. Instead it loads the metadata and you can load whatever you want from your bucket for further processing

- Generate key pair and custom config file with lustre file system

```
# generate a new keypair, remove those lines if you want to use the previous one
aws ec2 create-key-pair --key-name lab-4-your-key --query KeyMaterial --output text > ~/.ssh/lab-4-key
chmod 600 ~/.ssh/lab-4-key

# create the cluster configuration
IFACE=$(curl --silent http://169.254.169.254/latest/meta-data/network/interfaces/macs/)
SUBNET_ID=$(curl --silent http://169.254.169.254/latest/meta-data/network/interfaces/macs/${IFACE}/subnet-id)
VPC_ID=$(curl --silent http://169.254.169.254/latest/meta-data/network/interfaces/macs/${IFACE}/vpc-id)
AZ=$(curl http://169.254.169.254/latest/meta-data/placement/availability-zone)
REGION=${AZ::-1}


mkdir -p ~/.parallelcluster
cat > ~/.parallelcluster/config << EOF
[aws]
aws_region_name = ${REGION}

[global]
cluster_template = default
update_check = false
sanity_check = false

[cluster default]
key_name = lab-4-your-key
vpc_settings = public
base_os = alinux2
ebs_settings = myebs
fsx_settings = myfsx
compute_instance_type = c5.18xlarge
master_instance_type = c5.xlarge
cluster_type = ondemand
placement_group = DYNAMIC
placement = compute
max_queue_size = 8
initial_queue_size = 0
disable_hyperthreading = true
scheduler = slurm

[vpc public]
vpc_id = ${VPC_ID}
master_subnet_id = ${SUBNET_ID}

[ebs myebs]
shared_dir = /shared
volume_type = gp2
volume_size = 20

[fsx myfsx]
shared_dir = /lustre
storage_capacity = 1200
import_path =  s3://mybucket-${BUCKET_POSTFIX}
deployment_type = SCRATCH_2

[aliases]
ssh = ssh {CFN_USER}@{MASTER_IP} {ARGS}
EOF
```

- List files that lustre has access to

```
lfs find /lustre
```

- Check how much data is stored in the lustre folder (very little while data is 'released'; larger when it is loaded)
```
lfs df -h
```

- Check state of S3 data in Lustre
```
lfs hsm_state /lustre/SEG_C3NA_Velocity.sgy
```

- Release loaded content
```
sudo lfs hsm_release /lustre/SEG_C3NA_Velocity.sgy
```

**STILL NEED TO LEARN HOW TO RUN CONTAINER WITHIN CLUSTER**
- To-Do Simulations with AWS batch lab
- To-Do Distributed Machine Learning lab
