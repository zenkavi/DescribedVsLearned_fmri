from argparse import ArgumentParser
import glob
import nibabel as nib
import os
import pickle
import pandas as pd
import sys

parser = ArgumentParser()
parser.add_argument("-c", "--contrast", help="contrast name")
args = parser.parse_args()
contrast_id = args.subnum

#################################
# Level 1
#################################

l1_out_path = os.environ['L1_OUT_PATH']
l1_code_path = os.environ['L1_CODE_PATH']

glms = glob.glob(os.path.join(l1_out_path, '*/*.pkl'))
desmats = glob.glob(os.path.join(l1_out_path, '*/*.csv'))

for cur_glm, cur_desmat in zip(glms, desmats):

    subnum = re.findall('\d+', os.path.basename(cur_glm))[0]
    subnum = re.findall('\d+', os.path.basename(cur_glm))[1]

    f = open(cur_glm, 'rb')
    fmri_glm = pickle.load(f)
    f.close()

    design_matrix = pd.read_csv(cur_desmat)
    if 'Unnamed: 0' in design_matrix.columns:
      design_matrix=design_matrix.drop(columns=['Unnamed: 0'])

    sys.path.append(l1_code_path)
    from level1_utils import make_contrasts

    contrasts = make_contrasts(design_matrix)

    contrast_val = contrasts[contrast_id]

    z_map = fmri_glm.compute_contrast(contrast_val, output_type='z_score')

    nib.save(z_map, '%s/contrasts/sub-%s_run-%s_%s.nii.gz'%(l1_out_path, subnum, runnum, contrast_id))
    print("***********************************************")
    print("Done saving contrasts for sub-%s run-%s"%(subnum, runnum))
    print("***********************************************")


#################################
# Level 2
#################################



#################################
# Level 3
#################################
