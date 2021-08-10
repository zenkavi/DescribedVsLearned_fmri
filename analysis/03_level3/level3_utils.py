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
from save_randomise_output import save_randomise_output
randomise = mem.cache(fsl.Randomise)

def run_level3(mnum, reg, sign, tfce, data_path, out_path, bm_path, c_thresh, num_perm, var_smooth, one):

    l2_in_path = "%s/sub-*/contrasts"%(data_path)

    reg_path = "%s/%s"%(out_path, reg)
    if not os.path.exists(reg_path):
        os.makedirs(reg_path)

    level2_images = glob.glob('%s/sub-*_%s.nii.gz'%(l2_in_path, reg))
    level2_images.sort()

    if os.path.exists('%s/all_l2_%s_%s.nii.gz'%(reg_path, mnum, reg)) == False or os.path.exists("%s/group_mask_%s_%s.nii.gz"%(reg_path,mnum,reg)) == False:
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
        nib.save(all_l2_images, '%s/all_l2_%s_%s.nii.gz'%(reg_path, mnum, reg))

        print("***********************************************")
        print("Making group_mask")
        print("***********************************************")
        brainmasks = glob.glob("%s/sub-*/func/*brain_mask.nii*"%(bm_path))
        mean_mask = mean_img(brainmasks)
        group_mask = math_img("a>=0.95", a=mean_mask)
        group_mask = resample_to_img(group_mask, all_l2_images, interpolation='nearest')
        group_mask.to_filename("%s/group_mask_%s_%s.nii.gz"%(reg_path,mnum,reg))
        print("***********************************************")
        print("Group mask saved for: %s %s"%(mnum, reg))
        print("***********************************************")

    if os.path.exists('%s/neg_all_l2_%s_%s.nii.gz'%(reg_path, mnum, reg)) == False:
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
        binaryMaths(in_file='%s/all_l2_%s_%s.nii.gz'%(reg_path, mnum, reg),
                    operation = "mul",
                    operand_value = -1,
                    out_file = '%s/neg_all_l2_%s_%s.nii.gz'%(reg_path, mnum, reg))

    if sign == "pos":
        in_file_name = "%s/all_l2_%s_%s.nii.gz"%(reg_path, mnum, reg)
    if sign == "neg":
        in_file_name = "%s/neg_all_l2_%s_%s.nii.gz"%(reg_path, mnum, reg)

    print("***********************************************")
    print("Beginning randomise")
    print("***********************************************")
    if mnum == "model1":
        randomise_results = randomise(in_file=in_file_name,
                                  mask= "%s/group_mask_%s_%s.nii.gz"%(reg_path, mnum, reg),
                                  one_sample_group_mean=one,
                                  tfce=tfce,
                                  c_thresh = c_thresh,
                                  vox_p_values=True,
                                  num_perm=num_perm,
                                  var_smooth = var_smooth)

    if mnum in ["model2", "model2_g"]:
        randomise_results = randomise(in_file=in_file_name,
                              mask= "%s/group_mask_%s_%s.nii.gz"%(out_path, mnum, reg),
                              design_mat = "%s/%s_design.mat"%(mnum_path, mnum),
                              tcon="%s/%s_design.con"%(mnum_path, mnum),
                              tfce=tfce,
                              c_thresh = c_thresh,
                              vox_p_values=True,
                              num_perm=num_perm,
                              var_smooth = var_smooth)

    if sign == "neg":
        save_randomise_output(randomise_results, reg_path, mnum+'_neg', reg, tfce)
    else:
        save_randomise_output(randomise_results, reg_path, mnum, reg, tfce)
