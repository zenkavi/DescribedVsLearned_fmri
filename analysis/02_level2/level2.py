#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from level2_utils import run_level2
import os

#Usage: ./level3.py -m MNUM -r REG -s SIGN -tf TFCE

parser = ArgumentParser()
parser.add_argument("--mnum", help="model number")
parser.add_argument("--mname", help="model name", default="overall-mean")
parser.add_argument("-r", "--reg", help="regressor name")
parser.add_argument("--reg_rt", help="regress rt", default=0)
parser.add_argument("-c", "--c_thresh", help="cluster_threshold", default=3)
parser.add_argument("-np", "--num_perm", help="number of permutations", default=5000)
parser.add_argument("-vs", "--var_smooth", help="variance smoothing", default=5)
parser.add_argument("-s", "--sign", help="calculate p values for positive or negative t's")
parser.add_argument("--package", help="fsl or nilearn for permuation testing")
args = parser.parse_args()

mnum = args.mnum
mname = args.mname

reg = args.reg
regress_rt = int(args.reg_rt)

c_thresh = int(args.c_thresh)
num_perm = int(args.num_perm)
var_smooth = int(args.var_smooth)
sign = args.sign
package = args.package

data_path = os.environ['DATA_PATH']
out_path = os.environ['OUT_PATH']
bm_path = os.environ['BM_PATH']

run_level2(mnum, mname, reg, regress_rt, sign, data_path, out_path, bm_path, package = package, c_thresh=c_thresh, num_perm=num_perm, var_smooth=var_smooth)
