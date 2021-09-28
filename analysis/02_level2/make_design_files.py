import numpy as np
import pandas as pd
import os

def make_design_files(mname, learner_info_path):

    #group_diff: fast vs slow learners difference maps
    #Design and contrast matrices based on https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/GLM#Two-Group_Difference_.28Two-Sample_Unpaired_T-Test.29
    if mname == "group_diff":
        learner_info = pd.read_csv(learner_info_path)
        learner_info = learner_info.sort_values(by=["subnum"])

        design_matrix = learner_info[['fast_learner', 'slow_learner']]
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

    #group_means: fast vs slow learners group maps
    if mname == "group_means":
        learner_info = pd.read_csv(learner_info_path)
        learner_info = learner_info.sort_values(by=["subnum"])

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
    print("Saving design matrix for %s"%(mname))
    print("***********************************************")
    np.savetxt('%s_design.mat'%(mname),design_matrix.values,fmt='%1.0f',header=deshdr,comments='')

    print("***********************************************")
    print("Saving contrast matrix for %s"%(mname))
    print("***********************************************")
    np.savetxt('%s_design.con'%(mname),contrast_matrix,fmt='%1.0f',header=conhdr,comments='')
