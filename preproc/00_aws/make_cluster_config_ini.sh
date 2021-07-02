#! /bin/zsh
alias aws='docker run --rm -it -v ~/.aws:/root/.aws amazon/aws-cli'
export REGION=`aws configure get region`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
export VPC_ID=`aws ec2 describe-vpcs | jq -j '.Vpcs[0].VpcId'`

cat > tmp.ini << EOF
[[aws]
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
master_instance_type = m5.xlarge
placement_group = DYNAMIC
placement = compute
scheduler = slurm
s3_read_write_resource = arn:aws:s3:::described-vs-experienced*
post_install = s3://described-vs-experienced/test-setup-env.sh

[compute_resource default]
instance_type = m5.2xlarge
disable_hyperthreading = true
min_count = 0
max_count = 8

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
