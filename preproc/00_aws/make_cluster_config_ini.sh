#! /bin/zsh
alias aws='docker run --rm -it -v ~/.aws:/root/.aws amazon/aws-cli'
export REGION=`aws configure get region`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
export VPC_ID=`aws ec2 describe-vpcs | jq -j '.Vpcs[0].VpcId'`

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
master_instance_type = c5.2xlarge
scheduler = slurm
queue_settings = compute
s3_read_write_resource = arn:aws:s3:::described-vs-experienced*
post_install = s3://described-vs-experienced/test-setup-env.sh
additional_iam_policies = arn:aws:iam::aws:policy/AmazonS3FullAccess
ebs_settings = myebs

[queue compute]
compute_resource_settings = default
placement_group = DYNAMIC
disable_hyperthreading = true

[compute_resource default]
instance_type = c5.4xlarge
min_count = 0
max_count = 8

[ebs myebs]
shared_dir = /shared
volume_type = gp2
volume_size = 50

[vpc public]
vpc_id = ${VPC_ID}
master_subnet_id = ${SUBNET_ID}

[aliases]
ssh = ssh {CFN_USER}@{MASTER_IP} {ARGS}
EOF
