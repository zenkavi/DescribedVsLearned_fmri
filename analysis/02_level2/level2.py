#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from level2_utils import run_level2
import os
#Usage: python level2.py -s SUBNUM -c CONTRAST --reg_rt REG_RT

parser = ArgumentParser()
parser.add_argument("-s", "--subnum", help="subject number")
parser.add_argument("-c", "--contrasts", default=None)
parser.add_argument("--mnum", help="model number")
parser.add_argument("--reg_rt", help="regress rt", default=1)
args = parser.parse_args()
subnum = args.subnum
mnum = args.mnum #not actually used; keeping for consistency with level1
contrasts = args.contrasts
reg_rt = args.reg_rt
data_path = os.environ['DATA_PATH']
out_path = os.environ['OUT_PATH']
l1_code_path = os.path.join(os.environ['CODE_PATH'], '01_level1')

run_level2(subnum, mnum, contrasts, data_path, out_path, regress_rt=reg_rt, l1_code_path=l1_code_path)
