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

def run_level2(mnum, mname, reg, regress_rt, sign, tfce, data_path, out_path, bm_path, package='fsl', from_cmaps = True, c_thresh=3, num_perm=1000, var_smooth=5):
    if package == 'fsl':
        fsl_randomise_level2(mnum, mname, reg, regress_rt, sign, tfce, data_path, out_path, bm_path, c_thresh=c_thresh, num_perm=num_perm, var_smooth=var_smooth)
    else:
        nilearn_level2(mnum, mname, reg, regress_rt, data_path, out_path, from_cmaps=True, num_perm=1000, var_smooth=5)

def nilearn_level2(mnum, mname, reg, regress_rt, data_path, out_path, from_cmaps=True, num_perm=1000, var_smooth=5):

    reg_path = "%s/%s_%s_reg-rt%s"%(out_path, reg, mnum, str(regress_rt))
    if not os.path.exists(reg_path):
        os.makedirs(reg_path)

    suffix = reg + '_' + mnum + '_reg-rt' + str(regress_rt)

    # Tutorial for running level 2 from parameter estimate maps
    # https://nilearn.github.io/auto_examples/05_glm_second_level/plot_second_level_one_sample_test.html#sphx-glr-auto-examples-05-glm-second-level-plot-second-level-one-sample-test-py
    if from_cmaps:
        input_path = "%s/sub-*/contrasts"%(data_path)

        level1_images = glob.glob('%s/sub-*_%s_reg-rt%s_%s_effect_size.nii.gz'%(input_path, mnum, str(regress_rt), reg))
        level1_images.sort()

        second_level_input = level1_images
        design_matrix = pd.DataFrame([1] * len(second_level_input), columns=['intercept'])

        second_level_model = SecondLevelModel(smoothing_fwhm=var_smooth)
        second_level_model = second_level_model.fit(second_level_input, design_matrix=design_matrix)

        z_map = second_level_model.compute_contrast(output_type='z_score')
        nib.save(z_map, '%s/%s_nilearn_unthresh_zmap.nii.gz'%(reg_path, suffix))

        print("Saved level2 unthresholded z-map for %s"%(suffix))

        # Additional Tutorial for permutation testing
        # https://nilearn.github.io/auto_examples/05_glm_second_level/plot_second_level_association_test.html#sphx-glr-auto-examples-05-glm-second-level-plot-second-level-association-test-py
        from nilearn.glm.second_level import non_parametric_inference
        # The neg-log p-values obtained with nonparametric testing are capped at 3 if the number of permutations is 1e3.
        neg_log_pvals_permuted_ols_unmasked = non_parametric_inference(second_level_input,
                             design_matrix=design_matrix,
                             model_intercept=True, n_perm=num_perm,
                             two_sided_test=False,
                             smoothing_fwhm=var_smooth, n_jobs=1, verbose=1)

        nib.save(neg_log_pvals_permuted_ols_unmasked, '%s/%s_nilearn_neg_log_pvals_permuted_ols_unmasked.nii.gz'%(reg_path, suffix))

    # Tutorial for running level 2 from FirstLevelObjects
    # https://nilearn.github.io/auto_examples/07_advanced/plot_bids_analysis.html#sphx-glr-auto-examples-07-advanced-plot-bids-analysis-py
    else:
        input_path = "%s/sub-*"%(data_path)

        level1_models = glob.glob('%s/sub-*_%s_reg-rt%s_level1_glm.pkl'%(input_path, mnum, str(regress_rt)))
        level1_models.sort()

        second_level_input = []
        for fn in level1_models:
            with open(fn, "rb") as input_file:
                l1_model = pickle.load(input_file)
                second_level_input.append(l1_model)

        second_level_model = SecondLevelModel(smoothing_fwhm=var_smooth)
        second_level_model = second_level_model.fit(second_level_input)

        z_map = second_level_model.compute_contrast(first_level_contrast= reg, output_type='z_score')
        nib.save(z_map, '%s/%s_nilearn_unthresh_zmap.nii.gz'%(reg_path, suffix))

        print("""
        Saved level2 unthresholded z-maps but no perumatation test was done for thresholding.
        non_parametric_inference function does not accept FirstLevelModel objects as input.
        It requires a list of level 1 contrast maps.
        Save the effect_size maps from level 1 first!
        """)



def flatten(t):
    return [item for sublist in t for item in sublist]

def save_randomise_output(randomise_results, reg_path, mname, suffix, tfce, sign):
    rand_files_list = [i for i in randomise_results.outputs.trait_get().values() if len(i)>0]
    rand_files_list = flatten(rand_files_list)

    for fn in rand_files_list:
        cur_file = suffix + '_' + sign + '_' + mname + '_' + os.path.basename(fn)
        shutil.move(fn, "%s/%s"%(reg_path, cur_file))

def fsl_randomise_level2(mnum, mname, reg, regress_rt, sign, tfce, data_path, out_path, bm_path, c_thresh=3, num_perm=1000, var_smooth=5):
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
                                  tfce=tfce,
                                  c_thresh = c_thresh,
                                  vox_p_values=True,
                                  num_perm=num_perm,
                                  var_smooth = var_smooth)

    if mname in ["group-diff", "group-means"]:
        randomise_results = randomise(in_file=in_file_name,
                              mask= "%s/group-mask_%s_%s.nii.gz"%(reg_path, mname, suffix),
                              design_mat = "/code/%s_design.mat"%(mname),
                              tcon="/code/%s_design.con"%(mname),
                              tfce=tfce,
                              c_thresh = c_thresh,
                              vox_p_values=True,
                              num_perm=num_perm,
                              var_smooth = var_smooth)

    save_randomise_output(randomise_results, reg_path, mname, suffix, tfce, sign)
