import glob
import nibabel as nib
import numpy as np
import os
import pickle
import pandas as pd
import sys
import re

def run_posthoc_contrast(contrast_id, l1_out_path, l1_code_path, l2_out_path, l2_code_path, l3_out_path, l3_code_path, bm_path, mnum, sign, tfce, c_thresh, num_perm, var_smooth, one):

    #################################
    # Level 1
    #################################

    # Read in contrast making function
    sys.path.append(l1_code_path)
    from level1_utils import make_contrasts

    glms = glob.glob(os.path.join(l1_out_path, '*/*.pkl'))
    glms.sort()
    desmats = glob.glob(os.path.join(l1_out_path, '*/*.csv'))
    desmats.sort()

    for cur_glm, cur_desmat in zip(glms, desmats):

        subnum = re.findall('\d+', os.path.basename(cur_glm))[0]
        runnum = re.findall('\d+', os.path.basename(cur_glm))[1]

        if (os.path.exists('%s/sub-%s/contrasts/sub-%s_run-%s_%s.nii.gz'%(l1_out_path, subnum, subnum, runnum, contrast_id)) == False):
            # Load level 1 glm
            f = open(cur_glm, 'rb')
            fmri_glm = pickle.load(f)
            f.close()

            # Load level 1 design matrix
            design_matrix = pd.read_csv(cur_desmat)
            if 'Unnamed: 0' in design_matrix.columns:
              design_matrix=design_matrix.drop(columns=['Unnamed: 0'])

            # Make contrasts based on the level 1 design matrix
            contrasts = make_contrasts(design_matrix)

            # Extract contrast of interest
            contrast_val = contrasts[contrast_id]

            # Computer contrast map for subjects and run
            z_map = fmri_glm.compute_contrast(contrast_val, output_type='z_score')

            nib.save(z_map, '%s/sub-%s/contrasts/sub-%s_run-%s_%s.nii.gz'%(l1_out_path, subnum, subnum, runnum, contrast_id))
            print("***********************************************")
            print("Done saving contrasts for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")


    #################################
    # Level 2
    #################################

    sys.path.append(l2_code_path)
    from level2_utils import run_level2

    glms = [os.path.basename(i) for i in glms]
    subnums = np.unique([re.findall('\d+', i)[0] for i in glms])
    subnums.sort()

    for cur_sub in subnums:
        if(os.path.exists('%s/%s/contrasts/sub-%s_%s.nii.gz'%(l2_out_path, subnum, cur_sub, contrast_id)) == False):
            run_level2(cur_sub, contrast_id, l1_out_path, l2_out_path)

    #################################
    # Level 3
    #################################

    sys.path.append(l3_code_path)
    from level3_utils import run_level3

    run_level3(mnum, contrast_id, sign, tfce, l2_out_path, l3_out_path, bm_path, c_thresh, num_perm, var_smooth, one)
