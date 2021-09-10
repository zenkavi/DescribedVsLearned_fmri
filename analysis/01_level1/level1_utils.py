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

    return contrasts

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
        regs = ['fractalProb_ev', 'stim_ev', 'choiceShift_st', 'reward_ev']

    if mnum == 'model1a':
        regs = ['fractalProb_ev', 'stim_ev', 'choiceShiftLeft_st', 'choiceShiftRight_st', 'reward_ev']

    if mnum == 'model2':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev','choiceShift_st', 'reward_ev']

    if mnum == 'model3':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev','choiceShift_st', 'valDiff_par', 'reward_ev']

    if mnum == 'model4':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st','valChosen_par', 'valUnchosen_par', 'reward_ev']

    if mnum == 'model5':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st','valDiffLottery_par', 'valDiffFractal_par', 'reward_ev']

    if mnum == 'model5a':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st','valDiffLotteryWeighted_par', 'valDiffFractalWeighted_par', 'reward_ev']

    if mnum == 'model5b':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st','valDiffLotteryLowPFrac_par', 'valDiffLotteryMedPFrac_par', 'valDiffLotteryHighPFrac_par', 'valDiffFractalLowPFrac_par', 'valDiffFractalMedPFrac_par', 'valDiffFractalHighPFrac_par','reward_ev']

    if mnum == 'model6':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valChosenLottery_par', 'valUnchosenLottery_par','valChosenFractal_par', 'valUnchosenFractal_par', 'reward_ev']

    if mnum == 'model6a':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valChosenLotteryWeighted_par', 'valUnchosenLotteryWeighted_par','valChosenFractalWeighted_par', 'valUnchosenFractalWeighted_par', 'reward_ev']

    if mnum == 'model7':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st','valDiffLottery_par', 'valDiffFractal_par', 'reward_ev', 'reward_par', 'rewardLeftFractal_par', 'rewardRightFractal_par','rpeLeftFractal_par', 'rpeRightFractal_par', 'ppe_par']

    return regs

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

def get_events(subnum, runnum, mnum, data_path, behavior_path, regress_rt=0):

    # Read in fmri events
    fn = os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-%s_events.tsv' %(subnum, subnum, runnum))
    events = pd.read_csv(fn, sep='\t')

    # Read in behavioral data with modeled value and RPE estimates
    behavior = pd.read_csv(behavior_path)

    # Extract the correct subnum and runnum from behavioral data
    run_behavior = behavior.query('subnum == %d & session == %d'%(int(subnum), int(runnum)))

    # Demean columns that might be used for parametric regressors
    demean_cols = ['probFractalDraw', 'leftBundleVal', 'rightBundleVal', 'leftLotteryEV', 'rightLotteryEV', 'leftQValue', 'rightQValue', 'reward', 'ppe', 'leftQVAdv', 'leftEVAdv', 'leftbundleValAdv', 'leftFractalRpe', 'rightFractalRpe', 'valChosen', 'valUnchosen', 'valChosenLottery', 'valUnchosenLottery', 'valChosenFractal', 'valUnchosenFractal', 'leftFractalReward', 'rightFractalReward']
    demean_df = run_behavior[demean_cols]
    demean_df = demean_df - demean_df.mean()

    # Get regressors for the model
    regs = get_model_regs(mnum)

    # Get mean durations if parametric rt regressors will be included
    if regress_rt:
        # mean_rt = float(np.mean(events.query('trial_type == "stimulus"')[['duration']]))
        mean_rt = 1.29 # mean rt for all trials across all subjects

        cond_stim_rt = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
        cond_stim_rt['duration'] = mean_rt
        cond_stim_rt['trial_type'] = 'stim_rt'
        cond_stim_rt['modulation'] = events.query('trial_type == "stimulus"')[['duration']].reset_index(drop=True) - mean_rt

    for reg in regs:
        if reg == "fractalProb_ev":
            cond_fractalProb_ev = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_fractalProb_ev['trial_type'] = 'fractalProb_ev'
            cond_fractalProb_ev['modulation'] = 1

        if reg == "fractalProb_par":
            cond_fractalProb_par = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_fractalProb_par['trial_type'] = 'fractalProb_par'
            cond_fractalProb_par['modulation'] = demean_df['probFractalDraw'].reset_index(drop=True)

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
            cond_valChosen_par['modulation'] = demean_df['valChosen'].reset_index(drop=True)

        if reg == 'valUnchosen_par':
            if regress_rt:
                cond_valUnchosen_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosen_par['duration'] = mean_rt
            else:
                cond_valUnchosen_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosen_par['trial_type'] = 'valUnchosen_par'
            cond_valUnchosen_par['modulation'] = demean_df['valUnchosen'].reset_index(drop=True)

        if reg == 'valChosenLottery_par':
            if regress_rt:
                cond_valChosenLottery_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosenLottery_par['duration'] = mean_rt
            else:
                cond_valChosenLottery_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenLottery_par['trial_type'] = 'valChosenLottery_par'
            cond_valChosenLottery_par['modulation'] = demean_df['valChosenLottery'].reset_index(drop=True)

        if reg == 'valUnchosenLottery_par':
            if regress_rt:
                cond_valUnchosenLottery_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosenLottery_par['duration'] = mean_rt
            else:
                cond_valUnchosenLottery_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosenLottery_par['trial_type'] = 'valUnchosenLottery_par'
            cond_valUnchosenLottery_par['modulation'] = demean_df['valUnchosenLottery'].reset_index(drop=True)

        if reg == 'valChosenFractal_par':
            if regress_rt:
                cond_valChosenFractal_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosenFractal_par['duration'] = mean_rt
            else:
                cond_valChosenFractal_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenFractal_par['trial_type'] = 'valChosenFractal_par'
            cond_valChosenFractal_par['modulation'] = demean_df['valChosenFractal'].reset_index(drop=True)

        if reg == 'valUnchosenFractal_par':
            if regress_rt:
                cond_valUnchosenFractal_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosenFractal_par['duration'] = mean_rt
            else:
                cond_valUnchosenFractal_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosenFractal_par['trial_type'] = 'valUnchosenFractal_par'
            cond_valUnchosenFractal_par['modulation'] = demean_df['valUnchosenFractal'].reset_index(drop=True)

        if reg == "valChosenLotteryWeighted_par":
            if regress_rt:
                cond_valChosenLotteryWeighted_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosenLotteryWeighted_par['duration'] = mean_rt
            else:
                cond_valChosenLotteryWeighted_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenLotteryWeighted_par['trial_type'] = 'valChosenLotteryWeighted_par'
            cond_valChosenLotteryWeighted_par['modulation'] = np.array((1-run_behavior['wpFrac'])*demean_df['valChosenLottery'])

        if reg == "valUnchosenLotteryWeighted_par":
            if regress_rt:
                cond_valUnchosenLotteryWeighted_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosenLotteryWeighted_par['duration'] = mean_rt
            else:
                cond_valUnchosenLotteryWeighted_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosenLotteryWeighted_par['trial_type'] = 'valUnchosenLotteryWeighted_par'
            cond_valUnchosenLotteryWeighted_par['modulation'] = np.array((1-run_behavior['wpFrac'])*demean_df['valUnchosenLottery'])

        if reg == "valChosenFractalWeighted_par":
            if regress_rt:
                cond_valChosenFractalWeighted_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosenFractalWeighted_par['duration'] = mean_rt
            else:
                cond_valChosenFractalWeighted_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenFractalWeighted_par['trial_type'] = 'valChosenFractalWeighted_par'
            cond_valChosenFractalWeighted_par['modulation'] = np.array((run_behavior['wpFrac'])*demean_df['valChosenFractal'])

        if reg == "valUnchosenFractalWeighted_par":
            if regress_rt:
                cond_valUnchosenFractalWeighted_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valUnchosenFractalWeighted_par['duration'] = mean_rt
            else:
                cond_valUnchosenFractalWeighted_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosenFractalWeighted_par['trial_type'] = 'valUnchosenFractalWeighted_par'
            cond_valUnchosenFractalWeighted_par['modulation'] = np.array((run_behavior['wpFrac'])*demean_df['valUnchosenFractal'])

        if reg == 'valDiff_par':
            if regress_rt:
                cond_valDiff_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiff_par['duration'] = mean_rt
            else:
                cond_valDiff_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiff_par['trial_type'] = 'valDiff_par'
            cond_valDiff_par['modulation'] = demean_df['leftbundleValAdv'].reset_index(drop=True)

        if reg == 'valDiffLottery_par':
            if regress_rt:
                cond_valDiffLottery_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffLottery_par['duration'] = mean_rt
            else:
                cond_valDiffLottery_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffLottery_par['trial_type'] = 'valDiffLottery_par'
            cond_valDiffLottery_par['modulation'] = demean_df['leftEVAdv'].reset_index(drop=True)

        if reg == 'valDiffFractal_par':
            if regress_rt:
                cond_valDiffFractal_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffFractal_par['duration'] = mean_rt
            else:
                cond_valDiffFractal_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffFractal_par['trial_type'] = 'valDiffFractal_par'
            cond_valDiffFractal_par['modulation'] = demean_df['leftQVAdv'].reset_index(drop=True)

        if reg == "valDiffLotteryWeighted_par":
            if regress_rt:
                cond_valDiffLotteryWeighted_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffLotteryWeighted_par['duration'] = mean_rt
            else:
                cond_valDiffLotteryWeighted_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffLotteryWeighted_par['trial_type'] = 'valDiffLotteryWeighted_par'
            cond_valDiffLotteryWeighted_par['modulation'] = np.array(demean_df['leftEVAdv']*(1-run_behavior['wpFrac']))

        if reg == "valDiffFractalWeighted_par":
            if regress_rt:
                cond_valDiffFractalWeighted_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffFractalWeighted_par['duration'] = mean_rt
            else:
                cond_valDiffFractalWeighted_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffFractalWeighted_par['trial_type'] = 'valDiffFractalWeighted_par'
            cond_valDiffFractalWeighted_par['modulation'] = np.array(demean_df['leftQVAdv']*run_behavior['wpFrac'])

        if reg ==  "valDiffLotteryLowPFrac_par":
            if regress_rt:
                cond_valDiffLotteryLowPFrac_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffLotteryLowPFrac_par['duration'] = mean_rt
            else:
                cond_valDiffLotteryLowPFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffLotteryLowPFrac_par['trial_type'] = 'valDiffLotteryLowPFrac_par'
            cond_valDiffLotteryLowPFrac_par['modulation'] = np.array(np.where(run_behavior['probFractalDraw']<0.4, 1,0) * demean_df['leftEVAdv'])

        if reg ==  "valDiffLotteryMedPFrac_par":
            if regress_rt:
                cond_valDiffLotteryMedPFrac_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffLotteryMedPFrac_par['duration'] = mean_rt
            else:
                cond_valDiffLotteryMedPFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffLotteryMedPFrac_par['trial_type'] = 'valDiffLotteryMedPFrac_par'
            cond_valDiffLotteryMedPFrac_par['modulation'] = np.array(np.where( (run_behavior['probFractalDraw']>0.4) & (run_behavior['probFractalDraw']<0.7), 1,0) * demean_df['leftEVAdv'])

        if reg ==  "valDiffLotteryHighPFrac_par":
            if regress_rt:
                cond_valDiffLotteryHighPFrac_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffLotteryHighPFrac_par['duration'] = mean_rt
            else:
                cond_valDiffLotteryHighPFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffLotteryHighPFrac_par['trial_type'] = 'valDiffLotteryHighPFrac_par'
            cond_valDiffLotteryHighPFrac_par['modulation'] = np.array(np.where(run_behavior['probFractalDraw']>0.6, 1,0) * demean_df['leftEVAdv'])

        if reg ==  "valDiffFractalLowPFrac_par":
            if regress_rt:
                cond_valDiffFractalLowPFrac_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffFractalLowPFrac_par['duration'] = mean_rt
            else:
                cond_valDiffFractalLowPFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffFractalLowPFrac_par['trial_type'] = 'valDiffFractalLowPFrac_par'
            cond_valDiffFractalLowPFrac_par['modulation'] = np.array(np.where(run_behavior['probFractalDraw']<0.4, 1,0) * demean_df['leftQVAdv'])

        if reg ==  "valDiffFractalMedPFrac_par":
            if regress_rt:
                cond_valDiffFractalMedPFrac_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffFractalMedPFrac_par['duration'] = mean_rt
            else:
                cond_valDiffFractalMedPFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffFractalMedPFrac_par['trial_type'] = 'valDiffFractalMedPFrac_par'
            cond_valDiffFractalMedPFrac_par['modulation'] = np.array(np.where( (run_behavior['probFractalDraw']>0.4) & (run_behavior['probFractalDraw']<0.7), 1,0) * demean_df['leftQVAdv'])

        if reg ==  "valDiffFractalHighPFrac_par":
            if regress_rt:
                cond_valDiffFractalHighPFrac_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valDiffFractalHighPFrac_par['duration'] = mean_rt
            else:
                cond_valDiffFractalHighPFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffFractalHighPFrac_par['trial_type'] = 'valDiffFractalHighPFrac_par'
            cond_valDiffFractalHighPFrac_par['modulation'] = np.array(np.where(run_behavior['probFractalDraw']>0.6, 1,0) * demean_df['leftQVAdv'])

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

        if reg == 'choiceShiftLeft_st':
            cond_choiceShiftLeft_st = pd.DataFrame(events.query('trial_type == "stimulus"')['onset']+events.query('trial_type == "stimulus"')['duration'], columns = ['onset'])
            cond_choiceShiftLeft_st['duration'] = 0
            cond_choiceShiftLeft_st['trial_type'] = 'choiceShiftLeft_st'
            cond_choiceShiftLeft_st['modulation'] = np.where(run_behavior['choiceLeft'], 1, 0)

        if reg == 'choiceShiftRight_st':
            cond_choiceShiftRight_st = pd.DataFrame(events.query('trial_type == "stimulus"')['onset']+events.query('trial_type == "stimulus"')['duration'], columns = ['onset'])
            cond_choiceShiftRight_st['duration'] = 0
            cond_choiceShiftRight_st['trial_type'] = 'choiceShiftRight_st'
            cond_choiceShiftRight_st['modulation'] = np.where(run_behavior['choiceLeft'], 0, 1)

        if reg == 'reward_ev':
            cond_reward_ev = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_reward_ev['trial_type'] = 'reward_ev'
            cond_reward_ev['modulation'] = 1

        if reg == 'reward_par':
            cond_reward_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_reward_par['trial_type'] = 'reward_par'
            cond_reward_par['modulation'] = demean_df['reward'].reset_index(drop=True)

        if reg == 'ppe_par':
            cond_ppe_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_ppe_par['trial_type'] = 'ppe_par'
            cond_ppe_par['modulation'] = demean_df['ppe'].reset_index(drop=True)

        if reg == 'rewardLeftFractal_par':
            cond_rewardLeftFractal_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardLeftFractal_par['trial_type'] = 'rewardLeftFractal_par'
            cond_rewardLeftFractal_par['modulation'] = demean_df['leftFractalReward'].reset_index(drop=True)

        if reg == 'rewardRightFractal_par':
            cond_rewardRightFractal_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardRightFractal_par['trial_type'] = 'rewardRightFractal_par'
            cond_rewardRightFractal_par['modulation'] = demean_df['rightFractalReward'].reset_index(drop=True)

        if reg == "rpeLeftFractal_par":
            cond_rpeLeftFractal_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeLeftFractal_par['trial_type'] = 'rpeLeftFractal_par'
            cond_rpeLeftFractal_par['modulation'] = demean_df['leftFractalRpe'].reset_index(drop=True)

        if reg == "rpeRightFractal_par":
            cond_rpeRightFractal_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeRightFractal_par['trial_type'] = 'rpeRightFractal_par'
            cond_rpeRightFractal_par['modulation'] = demean_df['rightFractalRpe'].reset_index(drop=True)

    # List of var names including 'cond'
    toconcat = [i for i in dir() if 'cond' in i]
    tmp = {}
    for i in toconcat:
        tmp.update({i:locals()[i]})
    formatted_events = pd.concat(tmp, ignore_index=True)

    formatted_events = formatted_events.sort_values(by='onset')
    formatted_events = formatted_events[['onset', 'duration', 'trial_type', 'modulation']].reset_index(drop=True)
    return formatted_events

def make_level1_design_matrix(subnum, runnum, mnum, data_path, behavior_path, regress_rt=0, hrf_model = 'spm', drift_model='cosine'):

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

def run_level1(subnum, mnum, data_path, behavior_path, out_path, regress_rt=0, beta=False, noise_model='ar1', hrf_model='spm', drift_model='cosine',smoothing_fwhm=5):

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
