import glob
import nibabel as nib
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.first_level import make_first_level_design_matrix
import numpy as np
import os
import pandas as pd


def make_contrasts(design_matrix):
    # first generate canonical contrasts (i.e. regressors vs. baseline)
    contrast_matrix = np.eye(design_matrix.shape[1])
    contrasts = dict([(column, contrast_matrix[i])
                      for i, column in enumerate(design_matrix.columns)])

    dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
    
    wanted_keys = ['m1', 'm2', 'm3', 'm4', 'm1_ev', 'm2_ev', 'm3_ev', 'm4_ev', 'm1_rt', 'm2_rt', 'm3_rt', 'm4_rt','hpe', 'lpe','gain', 'loss','junk']
    
    contrasts = dictfilt(contrasts, wanted_keys)
    
    contrasts.update({'rt': (contrasts['m1_rt'] + contrasts['m2_rt'] + contrasts['m3_rt'] + contrasts['m4_rt'])})
    
    contrasts.update({'task_on': (contrasts['m1'] + contrasts['m2'] + contrasts['m3'] + contrasts['m4'])})

    return contrasts

def get_confounds(subnum, runnum, data_path, scrub_thresh = .5):
    
    fn = os.path.join(DATA_PATH, 'derivatives/sub-%s/func/sub-%s_task-bundles_run-%s_desc-confounds_timeseries.tsv'%(subnum, subnum, runnum))
    
    confounds = pd.read_csv(fn,  sep='\t')
    
    confound_cols = [x for x in confounds.columns if 'trans' in x]+[x for x in confounds.columns if 'rot' in x]+['std_dvars', 'framewise_displacement']
    
    formatted_confounds = confounds[confound_cols]
    
    formatted_confounds = formatted_confounds.fillna(0)
    
    formatted_confounds['scrub'] = np.where(formatted_confounds.framewise_displacement>scrub_thresh,1,0)
    
    formatted_confounds = formatted_confounds.assign(
        scrub = lambda dataframe: dataframe['framewise_displacement'].map(lambda framewise_displacement: 1 if framewise_displacement > scrub_thresh else 0))
    
    return formatted_confounds

def get_from_sidecar(subnum, runnum, keyname, data_path):
    
    fn = os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-%s_bold.json'%(subnum, subnum, runnum))
    f = open(fn)
    bold_sidecar = json.load(f)
    f.close()
    
    # Currently can only extract first level keys from the json. Can extract multiple first level keys.
    if type(keyname)==list:
        out = [bold_sidecar.get(key) for key in keyname]
    else:
        out = bold_sidecar[keyname]
    
    return out


def get_events(subnum, runnnum, data_path, behavior_path):
    
    # Read in fmri events
    fn = os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-%s_events.tsv' %(subnum, subnum, runnum))
    events = pd.read_csv(fn, sep='\t')
    
    # Read in behavioral data with modeled value and RPE estimates
    behavior = pd.read_csv(behavior_path)
    
    # Extract the correct subnum and runnum from behavioral data
    run_behavior = behavior.query('subnum == %d & session == %d'%(int(subnum), int(runnum)))
    
    # Regressors
    cond_cross = events.query('trial_type == "cross"')[['onset']]
    mean_cross_dur = float(np.mean(events.query('trial_type == "cross"')[['duration']]))
    cond_cross['duration'] = mean_cross_dur
    cond_cross['trial_type'] = "cross"
    cond_cross['modulation'] = 1
    
    cond_crossRt = events.query('trial_type == "cross"')[['onset']]
    cond_crossRt['duration'] = mean_cross_dur
    cond_crossRt['trial_type'] = "crossRt"
    cond_crossRt['modulation'] = events.query('trial_type == "cross"')[['duration']] - mean_cross_dur
    
    cond_fractalProb = events.query('trial_type == "fractalProb"')[['onset', 'duration']]
    cond_fractalProb['trial_type'] = 'fractalProb'
    cond_fractalProb['modulation'] = 1

    cond_fractalProbParam = events.query('trial_type == "fractalProb"')[['onset', 'duration']]
    cond_fractalProbParam['trial_type'] = 'fractalProbParam'
    cond_fractalProbParam = cond_fractalProbParam.reset_index(drop=True) 
    cond_fractalProbParam['modulation'] = run_behavior['probFractalDraw'] - np.mean(run_behavior['probFractalDraw'])
    
    cond_stim
    cond_stimRt
    cond_valDiff
    cond_choiceLeft
    cond_conflict
    cond_noconflict
    
    cond_reward
    cond_rewardParam
    cond_rpe
    
    cond_junk
    
    formatted_events = pd.concat([cond_.., cond_..,], ignore_index=True)

    formatted_events = formatted_events.sort_values(by='onset')

    formatted_events = formatted_events[['onset', 'duration', 'trial_type', 'modulation']].reset_index(drop=True)
    
    return formatted_events

def make_level1_design_matrix(subnum, runnum, data_path, hrf_model = 'spm', drift_model='cosine'):
    
    tr = get_from_sidecar(subnum, runnum, ['RepetitionTime'], data_path)
    n_scans = get_from_sidecar(subnum, runnum, ['dcmmeta_shape'], data_path)[3]
    frame_times = np.arange(n_scans) * tr 
    
    formatted_events = get_events(subnum, runnum)
    formatted_confounds = get_confounds(subnum, runnum)
    
    #takes care of derivative for condition columns if specified in hrf_model
    design_matrix = make_first_level_design_matrix(frame_times, 
                                               formatted_events, 
                                               drift_model=drift_model, 
                                               add_regs= formatted_confounds, 
                                               hrf_model=hrf_model)
    
    return design_matrix



def run_level1(subnum, beta):

    data_path = os.environ['DATA_PATH']
    out_path = os.path.join(data_path, "derivatives/nilearn/glm/level1/")
    
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    contrasts_path = os.path.join(out_path, "sub-%s/contrasts"%(subnum))
    if not os.path.exists(contrasts_path):
        os.makedirs(contrasts_path)
    
    sub_events = glob.glob(os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-*_events.tsv'%(subnum, subnum))
    sub_events.sort()

    for run_events in sub_events:

        runnum = re.findall('\d+', os.path.basename(run_events))[1]
        
        #fmri_img: path to preproc_bold that the model will be fit on
        fmri_img = os.path.join(data_path,"derivatives/fmriprep/sub-%s/func/sub-%s_task-bundles_run-%s_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"%(subnum, subnum, runnum))

        if os.path.isfile(fmri_img):

            #read in preproc_bold for that run
            cur_img_tr = get_from_sidecar(subnum, runnum, data_path, 'Re)

            #read in events.tsv for that run
            cur_events = pd.read_csv(run_events, sep = '\t')
            design_matrix = make_leve1_design_matrix(subnum, runnum)

            #define GLM parmeters
            fmri_glm = FirstLevelModel(t_r=cur_img_tr,
                                   noise_model='ar1',
                                   standardize=False,
                                   hrf_model='spm + derivative',
                                   drift_model='cosine',
                                   smoothing_fwhm=5,
                                   mask='%s/derivatives/fmriprep/sub-%s/func/sub-%s_task-machinegame_run-%s_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'%(data_path, subnum, subnum, runnum))

            #fit glm to run image using run events
            print("***********************************************")
            print("Running GLM for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            fmri_glm = fmri_glm.fit(fmri_img, design_matrices = design_matrix)

            print("***********************************************")
            print("Saving GLM for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            fn = os.path.join(out_path, 'sub-%s/sub-%s_run-%s_level1_glm.pkl' %(subnum, subnum, runnum))
            f = open(fn, 'wb')
            pickle.dump(fmri_glm, f)
            f.close()

            #Save design matrix
            design_matrix = fmri_glm.design_matrices_[0]
            print("***********************************************")
            print("Saving design matrix for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            design_matrix.to_csv(os.path.join(out_path, 'sub-%s/sub-%s_run-%s_level1_design_matrix.csv' %(subnum, subnum, runnum)))

            print("***********************************************")
            print("Running contrasts for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            contrasts = make_contrasts(design_matrix)
            for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
                z_map = fmri_glm.compute_contrast(contrast_val, output_type='z_score')
                nib.save(z_map, '%s/sub-%s_run-%s_%s.nii.gz'%(contrasts_path, subnum, runnum, contrast_id))
                if beta:
                    b_map = fmri_glm.compute_contrast(contrast_val, output_type='effect_size')
                    nib.save(b_map, '%s/sub-%s_run-%s_%s_betas.nii.gz'%(contrasts_path, subnum, runnum, contrast_id))
            print("***********************************************")
            print("Done saving contrasts for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")

        else:
            print("***********************************************")
            print("No pre-processed BOLD found for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")