#!/bin/bash

. "/etc/parallelcluster/cfnconfig"

case "${cfn_node_type}" in
    MasterServer)
        echo "This is the head node."
    ;;
    ComputeFleet)
        sudo yum update -y
        sudo amazon-linux-extras install docker
        sudo service docker start
        sudo usermod -a -G docker ec2-user
        docker pull nipy/heudiconv:0.9.0
    ;;
    *)
    ;;
esac
