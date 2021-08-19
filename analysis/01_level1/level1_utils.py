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
    to_filter = ['trans', 'rot', 'drift', 'framewise', 'scrub', 'constant', 'dvars']
    beh_regs = [x for x in beh_regs if all(y not in x for y in to_filter)]

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
        regs = ['cross_ev', 'fractalProb_ev', 'stim_ev', 'choice_st', 'reward_ev']

    if mnum == 'model1a':
        regs = ['cross_ev', 'fractalProb_ev', 'stim_ev', 'choiceShift_st', 'reward_ev']

    if mnum == 'model2':
        regs = ['cross_ev', 'fractalProb_ev', 'fractalProb_par', 'stim_ev','choice_st', 'reward_ev']

    if mnum == 'model3':
        regs = ['cross_ev', 'fractalProb_ev', 'fractalProb_par', 'stim_ev','choice_st', 'valDiff_par', 'reward_ev']

    if mnum == 'model4':
        regs = ['cross_ev', 'fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choice_st','valChosen_par', 'valUnchosen_par', 'reward_ev']

    if mnum == 'model5':
        regs = ['cross_ev', 'fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choice_st','valDiffLottery_par', 'valDiffFractal_par', 'reward_ev']

    if mnum == 'model6':
        regs = ['cross_ev', 'fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choice_st', 'valChosenLottery_par', 'valUnchosenLottery_par','valChosenFractal_par', 'valUnchosenFractal_par', 'reward_ev']

    return regs

def get_events(subnum, runnum, mnum, data_path, behavior_path, regress_rt=1):

    # Read in fmri events
    fn = os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-%s_events.tsv' %(subnum, subnum, runnum))
    events = pd.read_csv(fn, sep='\t')

    # Read in behavioral data with modeled value and RPE estimates
    behavior = pd.read_csv(behavior_path)

    # Extract the correct subnum and runnum from behavioral data
    run_behavior = behavior.query('subnum == %d & session == %d'%(int(subnum), int(runnum)))

    # Demean columns that might be used for parametric regressors
    demean_cols = ['probFractalDraw', 'leftBundleVal', 'rightBundleVal', 'leftLotteryEV', 'rightLotteryEV', 'leftQValue', 'rightQValue', 'reward', 'rpe', 'leftQVAdv', 'leftEVAdv', 'leftbundleValAdv']
    for cur_col in demean_cols:
        run_behavior.loc[:,cur_col].sub(run_behavior[cur_col].mean())

    # Get regressors for the model
    regs = get_model_regs(mnum)

    # Get mean durations if parametric rt regressors will be included
    if regress_rt:
        mean_cross_dur = float(np.mean(events.query('trial_type == "cross"')[['duration']]))
        mean_rt = float(np.mean(events.query('trial_type == "stimulus"')[['duration']]))

        cond_cross_rt = events.query('trial_type == "cross"')[['onset']].reset_index(drop=True)
        cond_cross_rt['duration'] = mean_cross_dur
        cond_cross_rt['trial_type'] = "cross_rt"
        cond_cross_rt['modulation'] = events.query('trial_type == "cross"')[['duration']].reset_index(drop=True) - mean_cross_dur

        cond_stim_rt = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
        cond_stim_rt['duration'] = mean_rt
        cond_stim_rt['trial_type'] = 'stim_rt'
        cond_stim_rt['modulation'] = events.query('trial_type == "stimulus"')[['duration']].reset_index(drop=True) - mean_rt

    for reg in regs:
        if reg == "cross_ev":
            if regress_rt:
                cond_cross_ev = events.query('trial_type == "cross"')[['onset']].reset_index(drop=True)
                cond_cross_ev['duration'] = mean_cross_dur
            else:
                cond_cross_ev = events.query('trial_type == "cross"')[['onset', 'duration']].reset_index(drop=True)
            cond_cross_ev['trial_type'] = "cross_ev"
            cond_cross_ev['modulation'] = 1

        if reg == "fractalProb_ev":
            cond_fractalProb_ev = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_fractalProb_ev['trial_type'] = 'fractalProb_ev'
            cond_fractalProb_ev['modulation'] = 1

        if reg == "fractalProb_par":
            cond_fractalProb_par = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_fractalProb_par['trial_type'] = 'fractalProb_par'
            cond_fractalProb_par['modulation'] = run_behavior['probFractalDraw'].reset_index(drop=True)

        if reg == "stim_ev":
            if regress_rt:
                cond_stim_ev = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_stim_ev['duration'] = mean_rt
            else:
                cond_stim_ev = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_stim_ev['trial_type'] = 'stim_ev'
            cond_stim_ev['modulation'] = 1

        if reg == 'valChosen_par':
            if regress_rt:
                cond_valChosen_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosen_par['duration'] = mean_rt
            else:
                cond_valChosen_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosen_par['trial_type'] = 'valChosen_par'
            cond_valChosen_par['modulation'] = np.where(run_behavior['choiceLeft'], run_behavior['leftBundleVal'], run_behavior['rightBundleVal'])

        if reg == 'valUnchosen_par':
            if regress_rt:
                cond_valUnchosen_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosen_par['duration'] = mean_rt
            else:
                cond_valUnchosen_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosen_par['trial_type'] = 'valUnchosen_par'
            cond_valUnchosen_par['modulation'] = np.where(run_behavior['choiceLeft']==0, run_behavior['leftBundleVal'], run_behavior['rightBundleVal'])

        if reg == 'valChosenLottery_par':
            if regress_rt:
                cond_valChosenLottery_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosenLottery_par['duration'] = mean_rt
            else:
                cond_valChosenLottery_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenLottery_par['trial_type'] = 'valChosenLottery_par'
            cond_valChosenLottery_par['modulation'] = np.where(run_behavior['choiceLeft'], run_behavior['leftLotteryEV'], run_behavior['rightLotteryEV'])

        if reg == 'valUnchosenLottery_par':
            if regress_rt:
                cond_valUnchosenLottery_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosenLottery_par['duration'] = mean_rt
            else:
                cond_valUnchosenLottery_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosenLottery_par['trial_type'] = 'valUnchosenLottery_par'
            cond_valUnchosenLottery_par['modulation'] = np.where(run_behavior['choiceLeft']==0, run_behavior['leftLotteryEV'], run_behavior['rightLotteryEV'])

        if reg == 'valChosenFractal_par':
            if regress_rt:
                cond_valChosenFractal_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosenFractal_par['duration'] = mean_rt
            else:
                cond_valChosenFractal_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenFractal_par['trial_type'] = 'valChosenFractal_par'
            cond_valChosenFractal_par['modulation'] = np.where(run_behavior['choiceLeft'], run_behavior['leftQValue'], run_behavior['rightQValue'])

        if reg == 'valUnchosenFractal_par':
            if regress_rt:
                cond_valUnchosenFractal_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosenFractal_par['duration'] = mean_rt
            else:
                cond_valUnchosenFractal_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosenFractal_par['trial_type'] = 'valUnchosenFractal_par'
            cond_valUnchosenFractal_par['modulation'] = np.where(run_behavior['choiceLeft']==0, run_behavior['leftQValue'], run_behavior['rightQValue'])

        if reg == 'valDiff_par':
            if regress_rt:
                cond_valDiff_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiff_par['duration'] = mean_rt
            else:
                cond_valDiff_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiff_par['trial_type'] = 'valDiff_par'
            cond_valDiff_par['modulation'] = run_behavior['leftbundleValAdv'].reset_index(drop=True)

        if reg == 'valDiffLottery_par':
            if regress_rt:
                cond_valDiffLottery_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffLottery_par['duration'] = mean_rt
            else:
                cond_valDiffLottery_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffLottery_par['trial_type'] = 'valDiffLottery_par'
            cond_valDiffLottery_par['modulation'] = run_behavior['leftEVAdv'].reset_index(drop=True)

        if reg == 'valDiffFractal_par':
            if regress_rt:
                cond_valDiffFractal_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffFractal_par['duration'] = mean_rt
            else:
                cond_valDiffFractal_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffFractal_par['trial_type'] = 'valDiffFractal_par'
            cond_valDiffFractal_par['modulation'] = run_behavior['leftQVAdv'].reset_index(drop=True)

        if reg == 'conflict_ev':
            if regress_rt:
                cond_conflict_ev = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_conflict_ev['duration'] = mean_rt
            else:
                cond_conflict_ev = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_conflict_ev['trial_type'] = 'conflict_ev'
            cond_conflict_ev['modulation'] = np.where(run_behavior['conflictTrial'] == "conflict", 1, 0)

        if reg == 'noConflict_ev':
            if regress_rt:
                cond_noConflict_ev = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_noConflict_ev['duration'] = mean_rt
            else:
                cond_noConflict_ev = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_noConflict_ev['trial_type'] = 'noConflict_ev'
            cond_noConflict_ev['modulation'] = np.where(run_behavior['conflictTrial'] == "no conflict", 1, 0)

        if reg == 'choice_st':
            cond_choice_st = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
            cond_choice_st['duration'] = 0
            cond_choice_st['trial_type'] = 'choice_st'
            cond_choice_st['modulation'] = 1

        if reg == 'choiceShift_st':
            cond_choiceShift_st = pd.DataFrame(events.query('trial_type == "stimulus"')['onset']+events.query('trial_type == "stimulus"')['duration'], columns = ['onset'])
            cond_choiceShift_st['duration'] = 0
            cond_choiceShift_st['trial_type'] = 'choiceShift_st'
            cond_choiceShift_st['modulation'] = 1

        if reg == 'reward_ev':
            cond_reward_ev = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_reward_ev['trial_type'] = 'reward_ev'
            cond_reward_ev['modulation'] = 1

        if reg == 'reward_par':
            cond_reward_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_reward_par['trial_type'] = 'reward_par'
            cond_reward_par['modulation'] = run_behavior['reward'].reset_index(drop=True)

        if reg == 'rpe_par':
            cond_rpe_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpe_par['trial_type'] = 'rpe_par'
            cond_rpe_par['modulation'] = run_behavior['rpe'].reset_index(drop=True)

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
            design_matrix.to_csv(os.path.join(out_path, 'sub-%s/sub-%s_run-%s_%s_reg-rt%s_level1_design_matrix.csv' %(subnum, subnum, runnum, mnum, str(regress_rt))), index=False)

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
            fn = os.path.join(out_path, 'sub-%s/sub-%s_run-%s_%s_reg-rt%s_level1_glm.pkl' %(subnum, subnum, runnum, mnum, str(regress_rt)))
            f = open(fn, 'wb')
            pickle.dump(fmri_glm, f)
            f.close()

            print("***********************************************")
            print("Running contrasts for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            contrasts = make_contrasts(design_matrix)
            for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
                z_map = fmri_glm.compute_contrast(contrast_val, output_type='z_score')
                nib.save(z_map, '%s/sub-%s_run-%s_%s_reg-rt%s_%s.nii.gz'%(contrasts_path, subnum, runnum, mnum, str(regress_rt), contrast_id))
                if beta:
                    b_map = fmri_glm.compute_contrast(contrast_val, output_type='effect_size')
                    nib.save(b_map, '%s/sub-%s_run-%s_%s_reg-rt%s_%s_betas.nii.gz'%(contrasts_path, subnum, runnum, mnum, str(regress_rt), contrast_id))
            print("***********************************************")
            print("Done saving contrasts for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")

        else:
            print("***********************************************")
            print("No pre-processed BOLD found for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
