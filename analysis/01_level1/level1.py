#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
from level1_utils import run_level1
import os

parser = ArgumentParser()
parser.add_argument("-s", "--subnum", help="subject number")
parser.add_argument("--mnum", help="model number")
parser.add_argument("--reg_rt", help="regress rt", default=0)
parser.add_argument("--save_contrast", default="True")
parser.add_argument("--output_type", default='effect_size')

args = parser.parse_args()

subnum = args.subnum
mnum = args.mnum
reg_rt = int(args.reg_rt)
save_contrast = args.save_contrast
if save_contrast == "True":
    save_contrast = True
output_type = args.output_type

data_path = os.environ['DATA_PATH']
behavior_path = os.environ['BEHAVIOR_PATH']
out_path = os.environ['OUT_PATH']

if mnum=='model12':
    behavior_path=os.path.join(behavior_path, 'all_trials_wBestRpe.csv')
elif 'model13' or 'model14' in mnum:
    behavior_path=os.path.join(behavior_path, 'all_trials_valSumComp.csv')
else:
    behavior_path=os.path.join(behavior_path, 'all_trials.csv')

run_level1(subnum, mnum, data_path, behavior_path, out_path, regress_rt = reg_rt, save_contrast = save_contrast, output_type=output_type)
