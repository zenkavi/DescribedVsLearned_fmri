#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from level1_utils import run_level1
import os
#Usage: python level1.py -s SUBNUM

parser = ArgumentParser()
parser.add_argument("-s", "--subnum", help="subject number")
parser.add_argument("--reg_rt", help="regress rt", default=1)
args = parser.parse_args()
subnum = args.subnum
reg_rt = args.reg_rt
data_path = os.environ['DATA_PATH']
behavior_path = os.environ['BEHAVIOR_PATH']
out_path = os.environ['OUT_PATH']

run_level1(subnum, data_path, behavior_path, out_path, regress_rt = reg_rt)
