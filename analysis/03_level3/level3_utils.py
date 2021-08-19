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

def run_level3(mnum, mname, reg, regress_rt, sign, tfce, data_path, out_path, bm_path, c_thresh, num_perm, var_smooth):

    l2_in_path = "%s/sub-*/contrasts"%(data_path)

    reg_path = "%s/%s_%s_reg-rt%s"%(out_path, reg, mnum, str(regress_rt))
    if not os.path.exists(reg_path):
        os.makedirs(reg_path)

    level2_images = glob.glob('%s/sub-*_%s_%s_reg-rt%s.nii.gz'%(l2_in_path, reg, mnum, str(regress_rt)))
    level2_images.sort()

    suffix = reg + '_' + mnum + '_reg-rt' + str(regress_rt)

    if os.path.exists('%s/all_l2_%s_%s.nii.gz'%(reg_path, mname, suffix)) == False or os.path.exists("%s/group_mask_%s_%s.nii.gz"%(reg_path, mname, suffix)) == False:
        print("***********************************************")
        print("Concatenating level 2 images for %s regressor %s"%(mname, suffix))
        print("***********************************************")
        smooth_l2s = []
        for l in level2_images:
            smooth_l2 = smooth_img(l, 5)
            smooth_l2s.append(smooth_l2)
        all_l2_images = concat_imgs(smooth_l2s, auto_resample=True)

        print("***********************************************")
        print("Saving level 2 images for %s regressor %s"%(mname, reg))
        print("***********************************************")
        nib.save(all_l2_images, '%s/all_l2_%s_%s.nii.gz'%(reg_path, mname, suffix))

        print("***********************************************")
        print("Making group_mask")
        print("***********************************************")
        brainmasks = glob.glob("%s/sub-*/func/*brain_mask.nii*"%(bm_path))
        mean_mask = mean_img(brainmasks)
        group_mask = math_img("a>=0.95", a=mean_mask)
        group_mask = resample_to_img(group_mask, all_l2_images, interpolation='nearest')
        group_mask.to_filename("%s/group_mask_%s_%s.nii.gz"%(reg_path,mname,suffix))
        print("***********************************************")
        print("Group mask saved for: %s %s"%(mname, reg))
        print("***********************************************")

    if os.path.exists('%s/neg_all_l2_%s_%s.nii.gz'%(reg_path, mname, suffix)) == False:
        print("***********************************************")
        print("Concatenating level 2 images for %s regressor %s"%(mname, suffix))
        print("***********************************************")
        smooth_l2s = []
        for l in level2_images:
            smooth_l2 = smooth_img(l, 5)
            smooth_l2s.append(smooth_l2)
        all_l2_images = concat_imgs(smooth_l2s, auto_resample=True)
        binaryMaths = mem.cache(fsl.BinaryMaths)
        print("***********************************************")
        print("Saving negative level 2 images for %s regressor %s"%(mname, reg))
        print("***********************************************")
        binaryMaths(in_file='%s/all_l2_%s_%s.nii.gz'%(reg_path, mname, suffix),
                    operation = "mul",
                    operand_value = -1,
                    out_file = '%s/neg_all_l2_%s_%s.nii.gz'%(reg_path, mname, suffix))

    if sign == "pos":
        in_file_name = "%s/all_l2_%s_%s.nii.gz"%(reg_path, mname, suffix)
    if sign == "neg":
        in_file_name = "%s/neg_all_l2_%s_%s.nii.gz"%(reg_path, mname, suffix)

    print("***********************************************")
    print("Beginning randomise")
    print("***********************************************")
    if mname == "overall_mean":
        randomise_results = randomise(in_file=in_file_name,
                                  mask= "%s/group_mask_%s_%s.nii.gz"%(reg_path, mname, suffix),
                                  one_sample_group_mean=True,
                                  tfce=tfce,
                                  c_thresh = c_thresh,
                                  vox_p_values=True,
                                  num_perm=num_perm,
                                  var_smooth = var_smooth)

    if mname in ["group_diff", "group_means"]:
        randomise_results = randomise(in_file=in_file_name,
                              mask= "%s/group_mask_%s_%s.nii.gz"%(reg_path, mname, reg),
                              design_mat = "/code/%s_design.mat"%(mname),
                              tcon="/code/%s_design.con"%(mname),
                              tfce=tfce,
                              c_thresh = c_thresh,
                              vox_p_values=True,
                              num_perm=num_perm,
                              var_smooth = var_smooth)

    if sign == "neg":
        save_randomise_output(randomise_results, reg_path, mname+'_neg', suffix, tfce)
    else:
        save_randomise_output(randomise_results, reg_path, mname, suffix, tfce)
