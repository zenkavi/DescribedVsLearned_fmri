# Usage: check_output.py --mnum 8 --reg_rt 0 --level 3
from argparse import ArgumentParser
import glob
import os
import sys

parser = ArgumentParser()
parser.add_argument("--mnum")
parser.add_argument("--reg", default=None)
parser.add_argument("--reg_rt")
parser.add_argument("--level")
parser.add_argument("--mname", default='overall-mean')
parser.add_argument("--l1_code_path", default='/shared/code/analysis/01_level1')
parser.add_argument("--out_path", default='/shared/bids_nifti_wface/derivatives/nilearn/glm')

args = parser.parse_args()
mnum = args.mnum
reg = args.reg
reg_rt = args.reg_rt
suffix = '%s_reg-rt%s'%(mnum, reg_rt)
level = int(args.level)
mname = args.mname
l1_code_path = args.l1_code_path
out_path = args.out_path

sys.path.append(l1_code_path)
from utils import get_model_regs_with_contrasts

if reg is not None:
    regs = [reg]
else:
    regs = get_model_regs_with_contrasts(mnum)
    if int(reg_rt):
        regs.append('stim_rt')

if not level == 3:
    subnums = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '23', '24', '25', '27']

if level == 1:

    runnums = ['1', '2', '3', '4', '5']

    for subnum in subnums:
        contrasts_path = os.path.join(out_path,'level1/%s/sub-%s/contrasts'%(suffix, subnum))
        counter = 0
        for runnum in runnums:

            check_path = os.path.join(out_path,'level1/%s/sub-%s/sub-%s_run-%s_%s_level1_design_matrix.csv'%(suffix, subnum, subnum, runnum, suffix))
            if not os.path.exists(check_path):
                print("File does not exist: %s"%(check_path))

            check_path = os.path.join(out_path,'level1/%s/sub-%s/sub-%s_run-%s_%s_level1_glm.pkl'%(suffix, subnum, subnum, runnum, suffix))
            if not os.path.exists(check_path):
                print("File does not exist: %s"%(check_path))

            for reg in regs:
                check_path = os.path.join(contrasts_path, 'sub-%s_run-%s_%s_%s.nii.gz'%(subnum, runnum, suffix, reg))
                if not os.path.exists(check_path):
                    print("File does not exist: %s"%(check_path))
                else:
                    counter = counter+1
        if counter == len(runnums) * len(regs):
            print("All level 1 contrast images in place for sub-%s"%(subnum))

if level == 2:

    for subnum in subnums:
        contrasts_path = os.path.join(out_path,'level2/%s/sub-%s/contrasts'%(suffix, subnum))

        counter = 0

        for reg in regs:
            check_path = os.path.join(out_path,'level2/%s/sub-%s/sub-%s_%s_%s_level2_glm.pkl'%(suffix, subnum, subnum, reg, suffix))
            if not os.path.exists(check_path):
                print("File does not exist: %s"%(check_path))

            check_path = os.path.join(contrasts_path, 'sub-%s_%s_%s.nii.gz'%(subnum, reg, suffix))
            if not os.path.exists(check_path):
                print("File does not exist: %s"%(check_path))
            else:
                counter = counter+1
        if counter == len(regs):
            print("All level 2 contrast images in place for sub-%s"%(subnum))

if level == 3:
    mname_files = {'overall-mean': ['all-l2_', 'group-mask_', 'neg_all-l2_', 'rand_tfce_corrp_tstat1_neg_', 'rand_tfce_corrp_tstat1_pos_', 'rand_tfce_tstat1_neg_', 'rand_tfce_tstat1_pos_'],
                   'group-diff': [],
                   'group-mean': []}

    mname_path = os.path.join(out_path,'level3/%s/%s'%(suffix, mname))

    for reg in regs:
        reg_path = os.path.join(mname_path, '%s_%s'%(reg, suffix))

        counter = 0
        for fn in mname_files[mname]:
            check_path = os.path.join(reg_path, fn+mname+'_'+reg+'_'+suffix+'.nii.gz')
            if not os.path.exists(check_path):
                print("File does not exist: %s"%(check_path))
            else:
                counter = counter+1
        if counter == len(mname_files[mname]):
            print("All level 3 files in place for %s_%s_%s"%(mname, suffix, reg))
