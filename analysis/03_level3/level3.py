#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from level3_utils import run_level3
import os

#Usage: ./level3.py -m MNUM -r REG -s SIGN -tf TFCE

parser = ArgumentParser()
parser.add_argument("-m", "--mnum", help="model number")
parser.add_argument("-r", "--reg", help="regressor name")
parser.add_argument("-tf", "--tfce", help="tfce", default=1)
parser.add_argument("-c", "--c_thresh", help="cluster_threshold", default=3)
parser.add_argument("-np", "--num_perm", help="number of permutations", default=1000)
parser.add_argument("-vs", "--var_smooth", help="variance smoothing", default=5)
parser.add_argument("-s", "--sign", help="calculate p values for positive or negative t's")
args = parser.parse_args()

mnum = args.mnum
if mnum == "model1":
    one = True

reg = args.reg

tfce = int(args.tfce)
if tfce == 1:
    tfce = True
else:
    tfce = False

c_thresh = int(args.c_thresh)
num_perm = int(args.num_perm)
var_smooth = int(args.var_smooth)
sign = args.sign

data_path = os.environ['DATA_PATH']
out_path = os.environ['OUT_PATH']
bm_path = os.environ['BM_PATH']

run_level3(mnum, reg, sign, tfce, data_path, out_path, bm_path, c_thresh, num_perm, var_smooth)
