import glob
import nibabel as nib
from nilearn.glm.second_level import SecondLevelModel
import numpy as np
import os
import pandas as pd
import pickle
import re
import sys

def run_level2(subnum, mnum, contrasts, data_path, out_path, regress_rt=0, l1_code_path):

    # mnum argument is not actually used bc paths include it in job submission but keeping it here for consistency
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    l2_contrasts_path = os.path.join(out_path,"sub-%s/contrasts"%(subnum))
    if not os.path.exists(l2_contrasts_path):
        os.makedirs(l2_contrasts_path)

    in_path = os.path.join(data_path, 'sub-%s/contrasts'%(subnum))
    sub_l1_contrasts = glob.glob(os.path.join(in_path, '*reg-rt%s*')%(str(regress_rt)))
    sub_l1_contrasts.sort()

    if contrasts == None:
        sys.path.append(l1_code_path)
        from utils import get_model_regs_with_contrasts
        contrasts = get_model_regs_with_contrasts(mnum)
        contrasts.sort()

    if isinstance(contrasts, str):
        contrasts = [contrasts]

    for c in contrasts:

        # Get level1's for all runs with this contrast
        second_level_input = [os.path.join(in_path,x) for x in sub_l1_contrasts if c in x]

        # 1's for all runs to get average for subject per contrast
        design_matrix = pd.DataFrame([1] * len(second_level_input), columns=['intercept'])
        model = SecondLevelModel(smoothing_fwhm=5.0)

        # Drop the suffix and add reg-rt info for saving file names
        c = c.split('.')[0]+'_%s_reg-rt%s'%(mnum,str(regress_rt))

        if len(second_level_input)>1:
            print("***********************************************")
            print("Running GLM for sub-%s contrast %s"%(subnum, c))
            print("***********************************************")
            model = model.fit(second_level_input, design_matrix=design_matrix)

            print("***********************************************")
            print("Saving GLM for sub-%s contrast %s"%(subnum, c))
            print("***********************************************")
            f = open('%s/sub-%s/sub-%s_%s_level2_glm.pkl' %(out_path,subnum, subnum, c), 'wb')
            pickle.dump(model, f)
            f.close()

            print("***********************************************")
            print("Running contrasts for sub-%s contrast %s"%(subnum, c))
            print("***********************************************")
            z_map = model.compute_contrast(output_type='z_score')

            nib.save(z_map, '%s/sub-%s_%s.nii.gz'%(l2_contrasts_path, subnum, c))
            print("***********************************************")
            print("Done saving contrasts for sub-%s contrast %s"%(subnum, c))
            print("***********************************************")

        elif len(second_level_input) == 1:
            print("***********************************************")
            print("1 level 1 image found for sub-%s contrast %s"%(subnum, c))
            print("Skipping level 2 for sub-%s contrast %s"%(subnum, c))
            print("Saving level 1 for level 2 for sub-%s contrast %s"%(subnum, c))
            z_map = nib.load(second_level_input[0])
            nib.save(z_map, '%s/sub-%s_%s.nii.gz'%(l2_contrasts_path, subnum, c))
            print("***********************************************")
        else:
            print("***********************************************")
            print("No level 1 image found for sub-%s contrast %s"%(subnum, c))
            print("***********************************************")
