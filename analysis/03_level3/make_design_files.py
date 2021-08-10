import glob
import numpy as np
import pandas as pd
import os
from argparse import ArgumentParser

data_loc = os.environ['DATA_LOC']
server_scripts = os.environ['SERVER_SCRIPTS']

def make_design_files(mnum, data_path, learner_info):

    mnum_path = "%s/derivatives/nilearn/level_3/%s"%(data_loc, mnum)
    l2_in_path = "%s/derivatives/nilearn/level_2/sub-*/contrasts"%(data_loc)
    level2_images = glob.glob('%s/sub-*_m1.nii.gz'%(l2_in_path))

    if not os.path.exists(mnum_path):
        os.makedirs(mnum_path)
    level2_images.sort()
    subs = [os.path.basename(x).split("_")[0] for x in level2_images]
    subs.sort()

    #model3: fast vs slow learners difference maps
    #Design and contrast matrices based on https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/GLM#Two-Group_Difference_.28Two-Sample_Unpaired_T-Test.29
    if mnum == "model2":
        learner_info = pd.read_csv('%s/nilearn/level_3/learner_info.csv'%(server_scripts))
        learner_info = learner_info.sort_values(by=["Sub_id"])
        learner_info = learner_info[learner_info.Sub_id.isin(subs)].reset_index(drop=True)
        design_matrix = learner_info[['fast_learner', 'slow_learner']]
        #design_matrix['intercept'] = [1] * len(level2_images)
        deshdr="""/NumWaves	2
/NumPoints	%s
/PPheights		1.000000e+00	1.000000e+00
/Matrix
        """%(str(design_matrix.shape[0]))
        conhdr = """/ContrastName1	fast_learner>slow_learner
/ContrastName2	fast_learner<slow_learner
/NumWaves	2
/NumContrasts	2
/PPheights		1.000000e+00	1.000000e+00
/Matrix
        """
        contrast_matrix = np.array([[1,-1],[-1,1]])

    #model3_g: fast vs slow learners group maps
    if mnum == "model2_g":
        learner_info = pd.read_csv('%s/nilearn/level_3/learner_info.csv'%(server_scripts))
        learner_info = learner_info.sort_values(by=["Sub_id"])
        learner_info = learner_info[learner_info.Sub_id.isin(subs)].reset_index(drop=True)
        design_matrix = learner_info[['fast_learner', 'slow_learner']]
        deshdr="""/NumWaves	2
/NumPoints	%s
/PPheights		1.000000e+00	1.000000e+00
/Matrix
        """%(str(design_matrix.shape[0]))
        conhdr = """/ContrastName1	fast_learner
/ContrastName2	slow_learner
/NumWaves	2
/NumContrasts	2
/PPheights		1.000000e+00	1.000000e+00
/Matrix
        """
        contrast_matrix = np.array([[1,0],[0,1]])

    print("***********************************************")
    print("Saving design matrix for %s"%(mnum))
    print("***********************************************")
    np.savetxt('%s/%s_design.mat'%(mnum_path, mnum),design_matrix.values,fmt='%1.0f',header=deshdr,comments='')

    print("***********************************************")
    print("Saving contrast matrix for %s"%(mnum))
    print("***********************************************")
    np.savetxt('%s/%s_design.con'%(mnum_path, mnum),contrast_matrix,fmt='%1.0f',header=conhdr,comments='')

    try:
        print("***********************************************")
        print("Saving design.fts for %s"%(mnum))
        print("***********************************************")
        np.savetxt('%s/%s_design.fts'%(mnum_path, mnum),design_fts,fmt='%1.0f',header=desfhdr,comments='')
    except NameError:
        print("***********************************************")
        print("No design.fts for %s!"%(mnum))
        print("***********************************************")
