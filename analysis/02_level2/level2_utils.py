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
import shutil

def run_level2(mnum, mname, reg, regress_rt, sign, data_path, out_path, bm_path, package='fsl', c_thresh=3, num_perm=1000, var_smooth=5):
    if package == 'fsl':
        fsl_randomise_level2(mnum, mname, reg, regress_rt, sign, data_path, out_path, bm_path, c_thresh=c_thresh, num_perm=num_perm, var_smooth=var_smooth)
    else:
        nilearn_level2(mnum, reg, regress_rt, sign, data_path, out_path, num_perm=num_perm, var_smooth=var_smooth)

def nilearn_level2(mnum, reg, regress_rt, sign, data_path, out_path, num_perm=5000, var_smooth=5):

    from nilearn.glm.second_level import SecondLevelModel

    reg_path = "%s/%s_%s_reg-rt%s"%(out_path, reg, mnum, str(regress_rt))
    if not os.path.exists(reg_path):
        os.makedirs(reg_path)

    suffix = reg + '_' + mnum + '_reg-rt' + str(regress_rt)

    # Tutorial for running level 2 from parameter estimate maps
    # https://nilearn.github.io/stable/auto_examples/05_glm_second_level/plot_second_level_one_sample_test.html#sphx-glr-auto-examples-05-glm-second-level-plot-second-level-one-sample-test-py
    input_path = "%s/sub-*/contrasts"%(data_path)

    level1_images = glob.glob('%s/sub-*_%s_reg-rt%s_%s_effect_size.nii.gz'%(input_path, mnum, str(regress_rt), reg))
    level1_images.sort()

    second_level_input = level1_images
    design_matrix = pd.DataFrame([1] * len(second_level_input), columns=['intercept'])

    # second_level_model = SecondLevelModel(smoothing_fwhm=var_smooth)
    # second_level_model = second_level_model.fit(second_level_input, design_matrix=design_matrix)

    # t_map = second_level_model.compute_contrast(output_type='stat')
    # nib.save(t_map, '%s/%s_nilearn_unthresh_tmap.nii.gz'%(reg_path, suffix))

    # print("Saved level2 unthresholded t-map for %s"%(suffix))

    # Additional Tutorial for permutation testing (saves unthresholded t image as well)

    suffix = suffix + '_' + str(sign)
    # https://nilearn.github.io/stable/auto_examples/05_glm_second_level/plot_second_level_association_test.html#sphx-glr-auto-examples-05-glm-second-level-plot-second-level-association-test-py
    from nilearn.glm.second_level import non_parametric_inference

    if sign == "neg":
        from nilearn.image import math_img
        second_level_input = [math_img("img*-1", img=i) for i in second_level_input]

    # The neg-log p-values obtained with nonparametric testing are capped at 3 if the number of permutations is 1e3.
    out_dict = non_parametric_inference(second_level_input,
                         design_matrix=design_matrix,
                         model_intercept=True, n_perm=num_perm,
                         two_sided_test=False, tfce = True,
                         smoothing_fwhm=var_smooth, n_jobs=7, verbose=1)

    #nib.save(neg_log_pvals_permuted_ols_unmasked, '%s/%s_nilearn_neg_log_pvals_permuted_ols_unmasked.nii.gz'%(reg_path, suffix))

    for k, v in out_dict.items():
        nib.save(v, '%s/%s_nilearn_%s.nii.gz'%(reg_path, suffix, k))

    print("Saved nilearn permutation test outputs for %s"%(suffix))


def flatten(t):
    return [item for sublist in t for item in sublist]

def save_randomise_output(randomise_results, reg_path, mname, suffix, sign):
    rand_files_list = [i for i in randomise_results.outputs.trait_get().values() if len(i)>0]
    rand_files_list = flatten(rand_files_list)

    for fn in rand_files_list:
        cur_file = suffix + '_' + sign + '_' + mname + '_' + os.path.basename(fn)
        shutil.move(fn, "%s/%s"%(reg_path, cur_file))

def fsl_randomise_level2(mnum, mname, reg, regress_rt, sign, data_path, out_path, bm_path, c_thresh=3, num_perm=1000, var_smooth=5):
    randomise = mem.cache(fsl.Randomise)

    input_path = "%s/sub-*/contrasts"%(data_path)

    reg_path = "%s/%s_%s_reg-rt%s"%(out_path, reg, mnum, str(regress_rt))
    if not os.path.exists(reg_path):
        os.makedirs(reg_path)

    level1_images = glob.glob('%s/sub-*_%s_reg-rt%s_%s_effect_size.nii.gz'%(input_path, mnum, str(regress_rt), reg))
    level1_images.sort()

    suffix = reg + '_' + mnum + '_reg-rt' + str(regress_rt)

    if os.path.exists('%s/all-l1_%s_%s_effect_size.nii.gz'%(reg_path, mname, suffix)) == False or os.path.exists("%s/group-mask_%s_%s.nii.gz"%(reg_path, mname, suffix)) == False:
        print("***********************************************")
        print("Concatenating level 1 images for %s regressor %s"%(mname, suffix))
        print("***********************************************")
        smooth_l1s = []
        for l in level1_images:
            smooth_l1 = smooth_img(l, 5)
            smooth_l1s.append(smooth_l1)
        all_l1_images = concat_imgs(smooth_l1s, auto_resample=True)

        print("***********************************************")
        print("Saving all subjects' level 1 images for %s regressor %s"%(mname, reg))
        print("***********************************************")
        nib.save(all_l1_images, '%s/all-l1_%s_%s_effect_size.nii.gz'%(reg_path, mname, suffix))

        print("***********************************************")
        print("Making group-mask")
        print("***********************************************")
        brainmasks = glob.glob("%s/sub-*/func/*brain_mask.nii*"%(bm_path))
        mean_mask = mean_img(brainmasks)
        group_mask = math_img("a>=0.95", a=mean_mask)
        group_mask = resample_to_img(group_mask, all_l1_images, interpolation='nearest')
        group_mask.to_filename("%s/group-mask_%s_%s.nii.gz"%(reg_path,mname,suffix))
        print("***********************************************")
        print("Group mask saved for: %s %s"%(mname, reg))
        print("***********************************************")

    if os.path.exists('%s/neg_all-l1_%s_%s_effect_size.nii.gz'%(reg_path, mname, suffix)) == False:
        print("***********************************************")
        print("Saving all subjects' negative level 1 images for %s regressor %s"%(mname, reg))
        print("***********************************************")
        binaryMaths = mem.cache(fsl.BinaryMaths)
        binaryMaths(in_file='%s/all-l1_%s_%s_effect_size.nii.gz'%(reg_path, mname, suffix),
                    operation = "mul",
                    operand_value = -1,
                    out_file = '%s/neg_all-l1_%s_%s_effect_size.nii.gz'%(reg_path, mname, suffix))

    if sign == "pos":
        in_file_name = "%s/all-l1_%s_%s_effect_size.nii.gz"%(reg_path, mname, suffix)
    if sign == "neg":
        in_file_name = "%s/neg_all-l1_%s_%s_effect_size.nii.gz"%(reg_path, mname, suffix)

    print("***********************************************")
    print("Beginning randomise")
    print("***********************************************")
    if mname == "overall-mean":
        randomise_results = randomise(in_file=in_file_name,
                                  mask= "%s/group-mask_%s_%s.nii.gz"%(reg_path, mname, suffix),
                                  one_sample_group_mean=True,
                                  tfce=True,
                                  c_thresh = c_thresh,
                                  vox_p_values=True,
                                  num_perm=num_perm,
                                  var_smooth = var_smooth)

    if mname in ["group-diff", "group-means"]:
        randomise_results = randomise(in_file=in_file_name,
                              mask= "%s/group-mask_%s_%s.nii.gz"%(reg_path, mname, suffix),
                              design_mat = "/code/%s_design.mat"%(mname),
                              tcon="/code/%s_design.con"%(mname),
                              tfce=True,
                              c_thresh = c_thresh,
                              vox_p_values=True,
                              num_perm=num_perm,
                              var_smooth = var_smooth)

    save_randomise_output(randomise_results, reg_path, mname, suffix, sign)
