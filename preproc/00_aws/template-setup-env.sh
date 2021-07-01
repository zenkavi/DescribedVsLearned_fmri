#!/bin/bash

. "/etc/parallelcluster/cfnconfig"

yum update -y
amazon-linux-extras install docker
service docker start
usermod -a -G docker ec2-user
chkconfig docker on
docker pull nipy/heudiconv:0.9.0
