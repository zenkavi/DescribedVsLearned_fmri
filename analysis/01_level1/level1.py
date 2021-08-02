#! /usr/bin/python3
from argparse import ArgumentParser
from level_1_utils import run_level1
import os
#Usage: python level_1.py -s SUBNUM -pe

parser = ArgumentParser()
parser.add_argument("-s", "--subnum", help="subject number")
args = parser.parse_args()
subnum = args.subnum
data_path = os.environ['DATA_PATH']
code_path = os.environ['CODE_PATH']
out_path = os.environ['OUT_PATH']

run_level1(subnum = subnum, out_path = "%s/sub-%s"%(out_path,subnum), pe=True, pe_path='...'%(...), beta=False, ev=False)
