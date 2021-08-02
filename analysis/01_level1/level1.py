#! /usr/bin/python3
from argparse import ArgumentParser
from level_1_utils import run_level1
import os
#Usage: python level_1.py -s SUBNUM -pe

parser = ArgumentParser()
parser.add_argument("-s", "--subnum", help="subject number")
args = parser.parse_args()
subnum = args.subnum
data_loc = os.environ['DATA_PATH']
code_path = os.environ['SERVER_SCRIPTS']

run_level1(subnum = subnum, out_path = "%s/derivatives/nilearn/level_1/sub-%s"%(data_loc,subnum), pe=True, pe_path='...'%(...), beta=False, ev=False)
