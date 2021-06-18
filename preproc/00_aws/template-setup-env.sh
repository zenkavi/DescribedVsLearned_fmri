#!/bin/bash

. "/etc/parallelcluster/cfnconfig"

case "${cfn_node_type}" in
    MasterServer)
        echo "This is the head node."
    ;;
    ComputeFleet)
        yum update -y
        amazon-linux-extras install docker
        service docker start
        usermod -a -G docker ec2-user
        chkconfig docker on
        docker pull nipy/heudiconv:0.9.0
    ;;
    *)
    ;;
esac
