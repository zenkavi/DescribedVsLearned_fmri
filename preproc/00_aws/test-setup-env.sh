#! /bin/bash
amazon-linux-extras install epel -y
yum install s3fs-fuse
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
chkconfig docker on
docker pull nipy/heudiconv:0.9.0

. "/etc/parallelcluster/cfnconfig"

if [[ "${cfn_node_type}" == "MasterServer" ]]
then
  mkdir ~/.out
  mkdir ~/.err
fi

aws s3 sync s3://described-vs-experienced/01_bidsify /scratch/01_bidsify
