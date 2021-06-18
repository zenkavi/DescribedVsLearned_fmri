#!/bin/bash

. "/etc/parallelcluster/cfnconfig"

case "${cfn_node_type}" in
    MasterServer)
        echo "This is the head node."
    ;;
    ComputeFleet)
        docker pull nipy/heudiconv:0.9.0
        docker pull poldracklab/mriqc:0.16.1
        docker pull poldracklab/fmriprep:20.2.0
    ;;
    *)
    ;;
esac
