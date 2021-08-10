#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
import os
#Usage: ./posthoc_contrast.py -c CONTRAST

import sys
code_path = os.environ['CODE_PATH']
sys.path.append(code_path)
from posthoc_contrasts_utils import run_posthoc_contrast

parser = ArgumentParser()
parser.add_argument("-c", "--contrast", help="contrast name")
parser.add_argument("-m", "--mnum", help="model number")
parser.add_argument("-tf", "--tfce", help="tfce", default=1)
parser.add_argument("-s", "--sign", help="calculate p values for positive or negative t's")
parser.add_argument("-ct", "--c_thresh", help="cluster_threshold", default=3)
parser.add_argument("-np", "--num_perm", help="number of permutations", default=1000)
parser.add_argument("-vs", "--var_smooth", help="variance smoothing", default=5)

args = parser.parse_args()
contrast_id = args.contrast

mnum = args.mnum
if mnum == "model1":
    one = True

tfce = int(args.tfce)
if tfce == 1:
    tfce = True
else:
    tfce = False

c_thresh = int(args.c_thresh)
num_perm = int(args.num_perm)
var_smooth = int(args.var_smooth)
sign = args.sign

l1_out_path = os.environ['L1_OUT_PATH']
l1_code_path = os.environ['L1_CODE_PATH']
l2_out_path = os.environ['L2_OUT_PATH']
l2_code_path = os.environ['L2_CODE_PATH']
l3_out_path = os.environ['L3_OUT_PATH']
l3_code_path = os.environ['L3_CODE_PATH']
bm_path = os.environ['BM_PATH']

run_posthoc_contrast(contrast_id, l1_out_path, l1_code_path, l2_out_path, l2_code_path, l3_out_path, l3_code_path, bm_path, mnum, sign, tfce, c_thresh, num_perm, var_smooth)
