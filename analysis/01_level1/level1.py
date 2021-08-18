#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from level1_utils import run_level1
import os

parser = ArgumentParser()
parser.add_argument("-s", "--subnum", help="subject number")
parser.add_argument("--mnum", help="model number")
parser.add_argument("--reg_rt", help="regress rt", default=1)
args = parser.parse_args()
subnum = args.subnum
mnum = args.mnum
reg_rt = int(args.reg_rt)
data_path = os.environ['DATA_PATH']
behavior_path = os.environ['BEHAVIOR_PATH']
out_path = os.environ['OUT_PATH']

run_level1(subnum, mnum, data_path, behavior_path, out_path, regress_rt = reg_rt)
