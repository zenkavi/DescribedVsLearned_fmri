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
parser.add_argument("--l2_package", default = "fsl")

args = parser.parse_args()
mnum = args.mnum
reg = args.reg
reg_rt = args.reg_rt
suffix = '%s_reg-rt%s'%(mnum, reg_rt)
level = int(args.level)
mname = args.mname
l1_code_path = args.l1_code_path
out_path = args.out_path
l2_package = args.l2_package

sys.path.append(l1_code_path)
from utils import get_model_regs_with_contrasts

if reg is not None:
    regs = [reg]
else:
    regs = get_model_regs_with_contrasts(mnum)
    if int(reg_rt):
        regs.append('stim_rt')

subnums = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '23', '24', '25', '27']

if level == 1:

    for subnum in subnums:
        contrasts_path = os.path.join(out_path,'level1/%s/sub-%s/contrasts'%(suffix, subnum))

        counter = 0

        for reg in regs:
            check_path = os.path.join(out_path,'level1/%s/sub-%s/sub-%s_%s_level1_glm.pkl'%(suffix, subnum, subnum, suffix))
            if not os.path.exists(check_path):
                print("File does not exist: %s"%(check_path))

            check_path = os.path.join(contrasts_path, 'sub-%s_%s_%s_effect_size.nii.gz'%(subnum, suffix, reg))
            if not os.path.exists(check_path):
                print("File does not exist: %s"%(check_path))
            else:
                counter = counter+1
        if counter == len(regs):
            print("All level 1 contrast images in place for sub-%s"%(subnum))

if level == 2:

    mname_path = os.path.join(out_path,'level2/%s/%s'%(suffix, mname))

    if l2_package == "fsl":
        mname_files = {'overall-mean': ['all-l1_', 'group-mask_', 'neg_all-l1_', 'neg_overall-mean_randomise_tfce_corrp_tstat1', 'neg_overall-mean_randomise_tstat1', 'pos_overall-mean_randomise_tfce_corrp_tstat1', 'pos_overall-mean_randomise_tstat1'],
                       'group-diff': [],
                       'group-mean': []}

        for reg in regs:
            reg_path = os.path.join(mname_path, '%s_%s'%(reg, suffix))

            counter = 0
            for fn in mname_files[mname]:
                if fn == 'all-l1_' or fn == 'neg_all-l1_':
                    check_path = os.path.join(reg_path, fn+mname+'_'+reg+'_'+suffix+'_effect_size.nii.gz')
                elif fn == 'group-mask_':
                    check_path = os.path.join(reg_path, fn+mname+'_'+reg+'_'+suffix+'.nii.gz')
                else:
                    check_path = os.path.join(reg_path, reg + '_' + suffix + '_' + fn +'.nii.gz')
                if not os.path.exists(check_path):
                    print("File does not exist: %s"%(check_path))
                else:
                    counter = counter+1
            if counter == len(mname_files[mname]):
                print("All level %s files in place for %s_%s_%s"%(str(counter), mname, suffix, reg))

    else:
        mname_files = {'overall-mean': ['_nilearn_unthresh_zmap.nii.gz', '_nilearn_neg_log_pvals_permuted_ols_unmasked.nii.gz'],
                       'group-diff': [],
                       'group-mean': []}

        for reg in regs:
            reg_path = os.path.join(mname_path, '%s_%s'%(reg, suffix))

            counter = 0
            for fn in mname_files[mname]:
                check_path = os.path.join(reg_path, reg + '_' + suffix + '_' + fn)
                if not os.path.exists(check_path):
                    print("File does not exist: %s"%(check_path))
                else:
                    counter = counter+1
            if counter == len(mname_files[mname]):
                print("All nilearn level %s files in place for %s_%s_%s"%(str(counter), mname, suffix, reg))
