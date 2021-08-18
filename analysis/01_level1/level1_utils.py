import glob
import json
import nibabel as nib
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.first_level import make_first_level_design_matrix
import numpy as np
import os
import pandas as pd
import re
import pickle

def make_contrasts(design_matrix):
    # first generate canonical contrasts (i.e. regressors vs. baseline)
    contrast_matrix = np.eye(design_matrix.shape[1])
    contrasts = dict([(column, contrast_matrix[i])
                      for i, column in enumerate(design_matrix.columns)])

    dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])

    beh_regs = design_matrix.columns
    beh_regs = [i for i in beh_regs if '_' not in i]
    beh_regs = [i for i in beh_regs if 'scrub' not in i]
    beh_regs = [i for i in beh_regs if 'constant' not in i]

    contrasts = dictfilt(contrasts, beh_regs)

    # Add on any additional contrasts
    # contrasts.update({'task-on': (contrasts['fractalProb'] + contrasts['conflict'] + contrasts['noconflict'] + contrasts['reward']),
    #                  'conflict-gt-noconflict': (contrasts['conflict'] - contrasts['noconflict']),
    #                  'valChosen-gt-valUnchosen': (contrasts['valChosen'] - contrasts['valUnchosen']),
    #                  'stim': (contrasts['conflict'] + contrasts['noconflict'])})

    return contrasts

def get_confounds(subnum, runnum, data_path, scrub_thresh = .5):

    fn = os.path.join(data_path, 'derivatives/fmriprep/sub-%s/func/sub-%s_task-bundles_run-%s_desc-confounds_timeseries.tsv'%(subnum, subnum, runnum))

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

def get_model_regs(mnum):
    if mnum == 'model1':
        regs = ['cross', 'fractalProb', 'stim', 'reward']

    if mnum == 'model2':
        regs [...]

    return regs

def get_events(subnum, runnum, mnum, data_path, behavior_path, regress_rt=1):

    # Read in fmri events
    fn = os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-%s_events.tsv' %(subnum, subnum, runnum))
    events = pd.read_csv(fn, sep='\t')

    # Read in behavioral data with modeled value and RPE estimates
    behavior = pd.read_csv(behavior_path)

    # Extract the correct subnum and runnum from behavioral data
    run_behavior = behavior.query('subnum == %d & session == %d'%(int(subnum), int(runnum)))

    # Get regressors for the model
    regs = get_model_regs(mnum)

    # Get mean durations if parametric rt regressors will be included
    if regress_rt:
        mean_cross_dur = float(np.mean(events.query('trial_type == "cross"')[['duration']]))
        mean_rt = float(np.mean(events.query('trial_type == "stimulus"')[['duration']]))

        cond_crossRt = events.query('trial_type == "cross"')[['onset']].reset_index(drop=True)
        cond_crossRt['duration'] = mean_cross_dur
        cond_crossRt['trial_type'] = "crossRt"
        cond_crossRt['modulation'] = events.query('trial_type == "cross"')[['duration']].reset_index(drop=True) - mean_cross_dur

        cond_stimRt = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
        cond_stimRt['duration'] = mean_rt
        cond_stimRt['trial_type'] = 'stimRt'
        cond_stimRt['modulation'] = events.query('trial_type == "stimulus"')[['duration']].reset_index(drop=True) - mean_rt

    for reg in regs:
        if reg == "cross":
            if regress_rt:
                cond_cross = events.query('trial_type == "cross"')[['onset']].reset_index(drop=True)
                cond_cross['duration'] = mean_cross_dur
            else:
                cond_cross = events.query('trial_type == "cross"')[['onset', 'duration']].reset_index(drop=True)
            cond_cross['trial_type'] = "cross"
            cond_cross['modulation'] = 1

        if reg == "fractalProb":
            cond_fractalProb = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_fractalProb['trial_type'] = 'fractalProb'
            cond_fractalProb['modulation'] = 1

        if reg == "fractalProbParam":
            cond_fractalProbParam = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_fractalProbParam['trial_type'] = 'fractalProbParam'
            cond_fractalProbParam['modulation'] = run_behavior['probFractalDraw'].sub(run_behavior['probFractalDraw'].mean()).reset_index(drop=True)

        if reg == "stim":
            ...

        if reg == 'valChosen':
            if regress_rt:
                cond_valChosen = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosen['duration'] = mean_rt
            else:
                cond_valChosen = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)\
            cond_valChosen['trial_type'] = 'valChosen'
            cond_valChosen['modulation'] = np.where(run_behavior['choiceLeft'], run_behavior['leftBundleVal'], 0)

        if reg == 'valUnchosen':
            if regress_rt:
                cond_valUnchosen = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosen['duration'] = mean_rt
            else:
                cond_valUnchosen = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosen['trial_type'] = 'valUnchosen'
            cond_valUnchosen['modulation'] = np.where(run_behavior['choiceLeft']==0, run_behavior['rightBundleVal'], 0)


        if reg == 'valChosenLottery':
            ...

        if reg == 'valUnchosenLottery':
            ...

        if reg == 'valChosenFractal':
            ...

        if reg == 'valUnchosenFractal':
            ...

        if reg == 'valDiff':
            ...

        if reg == 'valDiffLottery':
            ...

        if reg == 'valDiffFractals':
            ...

        if reg == 'conflict':
            if regress_rt:
                cond_conflict = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_conflict['duration'] = mean_rt
            else:
                cond_conflict = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_conflict['trial_type'] = 'conflict'
            cond_conflict['modulation'] = np.where(run_behavior['conflictTrial'] == "conflict", 1, 0)

        if reg == 'noConflict':
            if regress_rt:
                cond_noconflict = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_noconflict['duration'] = mean_rt
            else:
                cond_noconflict = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_noconflict['trial_type'] = 'noconflict'
            cond_noconflict['modulation'] = np.where(run_behavior['conflictTrial'] == "no conflict", 1, 0)

        if reg == 'choice':
            cond_choice = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
            cond_choice['duration'] = 0
            cond_choice['trial_type'] = 'choice'
            cond_choice['modulation'] = 1

        if reg == 'reward':
            cond_reward = events.query('trial_type == "reward"')[['onset', 'duration', 'trial_type']].reset_index(drop=True)
            cond_reward['modulation'] = 1

        if reg == 'rewardParam':
            cond_rewardParam = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardParam['trial_type'] = 'rewardParam'
            cond_rewardParam['modulation'] = run_behavior['reward'].sub(run_behavior['reward'].mean()).reset_index(drop=True)

        if reg == 'rpe':
            cond_rpe = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpe['trial_type'] = 'rpe'
            cond_rpe['modulation'] = run_behavior['rpe'].sub(run_behavior['rpe'].mean()).reset_index(drop=True)

    # List of var names including 'cond'
    toconcat = [i for i in dir() if 'cond' in i]
    tmp = {}
    for i in toconcat:
        tmp.update({i:locals()[i]})
    formatted_events = pd.concat(tmp, ignore_index=True)

    formatted_events = formatted_events.sort_values(by='onset')
    formatted_events = formatted_events[['onset', 'duration', 'trial_type', 'modulation']].reset_index(drop=True)
    return formatted_events

def make_level1_design_matrix(subnum, runnum, mnum, data_path, behavior_path, regress_rt=1, hrf_model = 'spm', drift_model='cosine'):

    tr = get_from_sidecar(subnum, runnum, 'RepetitionTime', data_path)
    n_scans = get_from_sidecar(subnum, runnum, 'dcmmeta_shape', data_path)[3]
    frame_times = np.arange(n_scans) * tr

    formatted_events = get_events(subnum, runnum, mnum, data_path, behavior_path, regress_rt=regress_rt)
    formatted_confounds = get_confounds(subnum, runnum, data_path)

    #takes care of derivative for condition columns if specified in hrf_model
    design_matrix = make_first_level_design_matrix(frame_times,
                                               formatted_events,
                                               drift_model=drift_model,
                                               add_regs= formatted_confounds,
                                               hrf_model=hrf_model)

    return design_matrix

def run_level1(subnum, mnum, data_path, behavior_path, out_path, regress_rt=1, beta=False, noise_model='ar1', hrf_model='spm', drift_model='cosine',smoothing_fwhm=5):

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    contrasts_path = os.path.join(out_path, "sub-%s/contrasts"%(subnum))
    if not os.path.exists(contrasts_path):
        os.makedirs(contrasts_path)

    sub_events = glob.glob(os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-*_events.tsv'%(subnum, subnum)))
    sub_events.sort()

    for run_events in sub_events:

        runnum = re.findall('\d+', os.path.basename(run_events))[1]

        #fmri_img: path to preproc_bold that the model will be fit on
        fmri_img = os.path.join(data_path,"derivatives/fmriprep/sub-%s/func/sub-%s_task-bundles_run-%s_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz"%(subnum, subnum, runnum))

        if os.path.isfile(fmri_img):

            #read in preproc_bold for that run
            cur_img_tr = get_from_sidecar(subnum, runnum, 'RepetitionTime', data_path)

            #read in events.tsv for that run
            cur_events = pd.read_csv(run_events, sep = '\t')
            design_matrix = make_level1_design_matrix(subnum, runnum, mnum, data_path, behavior_path, regress_rt=regress_rt, hrf_model = hrf_model, drift_model=drift_model)

            #Save design matrix
            print("***********************************************")
            print("Saving design matrix for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            design_matrix.to_csv(os.path.join(out_path, 'sub-%s/sub-%s_run-%s_reg-rt%s_level1_design_matrix.csv' %(subnum, subnum, runnum, str(regress_rt))), index=False)

            #define GLM parmeters
            mask_img = nib.load(os.path.join(data_path,'derivatives/fmriprep/sub-%s/func/sub-%s_task-bundles_run-%s_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'%(subnum, subnum, runnum)))
            fmri_glm = FirstLevelModel(t_r=cur_img_tr,
                                   noise_model=noise_model,
                                   standardize=False,
                                   hrf_model=hrf_model,
                                   drift_model=drift_model,
                                   smoothing_fwhm=smoothing_fwhm,
                                   mask_img=mask_img)

            #fit glm to run image using run events
            print("***********************************************")
            print("Running GLM for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            fmri_glm = fmri_glm.fit(fmri_img, design_matrices = design_matrix)

            print("***********************************************")
            print("Saving GLM for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            fn = os.path.join(out_path, 'sub-%s/sub-%s_run-%s_reg-rt%s_level1_glm.pkl' %(subnum, subnum, runnum, str(regress_rt)))
            f = open(fn, 'wb')
            pickle.dump(fmri_glm, f)
            f.close()

            print("***********************************************")
            print("Running contrasts for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            contrasts = make_contrasts(design_matrix)
            for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
                z_map = fmri_glm.compute_contrast(contrast_val, output_type='z_score')
                nib.save(z_map, '%s/sub-%s_run-%s_reg-rt%s_%s.nii.gz'%(contrasts_path, subnum, runnum, str(regress_rt), contrast_id))
                if beta:
                    b_map = fmri_glm.compute_contrast(contrast_val, output_type='effect_size')
                    nib.save(b_map, '%s/sub-%s_run-%s_reg-rt%s_%s_betas.nii.gz'%(contrasts_path, subnum, runnum, str(regress_rt), contrast_id))
            print("***********************************************")
            print("Done saving contrasts for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")

        else:
            print("***********************************************")
            print("No pre-processed BOLD found for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
