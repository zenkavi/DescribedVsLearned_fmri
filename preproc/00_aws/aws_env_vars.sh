#! /bin/zsh
alias aws='docker run --rm -it -v ~/.aws:/root/.aws amazon/aws-cli'
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
export VPC_ID=`aws ec2 describe-vpcs | jq -j '.Vpcs[0].VpcId'`
export MY_IP=`curl ifconfig.me`
export AMI_ID=ami-0b2ca94b5b49e0132
export KEY_NAME=test-cluster
export SG_ID=`aws ec2 describe-security-groups --filters Name=group-name,Values="test-cluster-sg"  | jq -j '.SecurityGroups[0].GroupId'`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
