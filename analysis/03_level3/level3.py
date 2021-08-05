#! /usr/bin/python3

from argparse import ArgumentParser
import glob
import nibabel as nib
from nilearn.image import concat_imgs, smooth_img, mean_img, math_img, resample_to_img
from  nipype.interfaces import fsl
from nipype.caching import Memory
mem = Memory(base_dir='.')
import numpy as np
import os
import pandas as pd
import pickle
import re
from save_randomise import save_randomise
randomise = mem.cache(fsl.Randomise)

#Usage: ./level_3.py -m MNUM -r REG


parser = ArgumentParser()
parser.add_argument("-m", "--mnum", help="model number")
parser.add_argument("-r", "--reg", help="regressor name")
parser.add_argument("-tf", "--tfce", help="tfce", action='store_true')
parser.add_argument("-c", "--c_thresh", help="cluster_threshold", default=3)
parser.add_argument("-np", "--num_perm", help="number of permutations", default=1000)
parser.add_argument("-vs", "--var_smooth", help="variance smoothing", default=5)
parser.add_argument("-s", "--sign", help="calculate p values for positive t's")

mnum = args.mnum
reg = args.reg
if mnum == "model1":
    one = True
tfce = args.tfce
c_thresh = int(args.c_thresh)
num_perm = int(args.num_perm)
var_smooth = int(args.var_smooth)

data_loc = os.environ['DATA_LOC']

l2_in_path = "%s/derivatives/nistats/level_2/sub-*/contrasts"%(data_loc)
mnum_path = "%s/derivatives/nistats/level_3/%s"%(data_loc,mnum)

out_path = "%s/%s"%(mnum_path,reg)
if not os.path.exists(out_path):
    os.makedirs(out_path)

level2_images = glob.glob('%s/sub-*_%s.nii.gz'%(l2_in_path, reg))
    level2_images.sort()

    if os.path.exists('%s/all_l2_%s_%s.nii.gz'%(out_path, mnum, reg)) == False or os.path.exists("%s/group_mask_%s_%s.nii.gz"%(out_path,mnum,reg)) == False:
    print("***********************************************")
    print("Concatenating level 2 images for %s regressor %s"%(mnum, reg))
    print("***********************************************")
    smooth_l2s = []
    for l in level2_images:
        smooth_l2 = smooth_img(l, 5)
        smooth_l2s.append(smooth_l2)
    all_l2_images = concat_imgs(smooth_l2s, auto_resample=True)
    print("***********************************************")
    print("Saving level 2 images for %s regressor %s"%(mnum, reg))
    print("***********************************************")
    nib.save(all_l2_images, '%s/all_l2_%s_%s.nii.gz'%(out_path, mnum, reg))
    print("***********************************************")
    print("Making group_mask")
    print("***********************************************")
    brainmasks = glob.glob("%s/derivatives/fmriprep_1.4.0/fmriprep/sub-*/func/*brain_mask.nii*"%(data_loc))
    mean_mask = mean_img(brainmasks)
    group_mask = math_img("a>=0.95", a=mean_mask)
    group_mask = resample_to_img(group_mask, all_l2_images, interpolation='nearest')
    group_mask.to_filename("%s/group_mask_%s_%s.nii.gz"%(out_path,mnum,reg))
    print("***********************************************")
    print("Group mask saved for: %s %s"%(mnum, reg))
    print("***********************************************")

if os.path.exists('%s/neg_all_l2_%s_%s.nii.gz'%(out_path, mnum, reg)) == False:
    print("***********************************************")
    print("Concatenating level 2 images for %s regressor %s"%(mnum, reg))
    print("***********************************************")
    smooth_l2s = []
    for l in level2_images:
        smooth_l2 = smooth_img(l, 5)
        smooth_l2s.append(smooth_l2)
    all_l2_images = concat_imgs(smooth_l2s, auto_resample=True)
    binaryMaths = mem.cache(fsl.BinaryMaths)
    print("***********************************************")
    print("Saving negative level 2 images for %s regressor %s"%(mnum, reg))
    print("***********************************************")
    binaryMaths(in_file='%s/all_l2_%s_%s.nii.gz'%(out_path, mnum, reg),
                operation = "mul",
                operand_value = -1,
                out_file = '%s/neg_all_l2_%s_%s.nii.gz'%(out_path, mnum, reg))

if sign == "pos":
    in_file_name = "%s/all_l2_%s_%s.nii.gz"%(out_path, mnum, reg)
if sign == "neg":
    in_file_name = "%s/neg_all_l2_%s_%s.nii.gz"%(out_path, mnum, reg)

print("***********************************************")
print("Beginning randomise")
print("***********************************************")
if mnum == "model1":
    randomise_results = randomise(in_file=in_file_name,
                              mask= "%s/group_mask_%s_%s.nii.gz"%(out_path, mnum, reg),
                              one_sample_group_mean=one,
                              tfce=tfce,
                              c_thresh = c_thresh,
                              vox_p_values=True,
                              num_perm=num_perm,
                              var_smooth = var_smooth)