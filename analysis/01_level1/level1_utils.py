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
from utils import get_from_sidecar, get_model_regs

def make_contrasts(design_matrix, mnum):
    # first generate canonical contrasts (i.e. regressors vs. baseline)
    contrast_matrix = np.eye(design_matrix.shape[1])
    contrasts = dict([(column, contrast_matrix[i])
                      for i, column in enumerate(design_matrix.columns)])

    dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])

    beh_regs = design_matrix.columns
    to_filter = ['trans', 'rot', 'drift', 'framewise', 'scrub', 'constant', 'dvars']
    beh_regs = [x for x in beh_regs if all(y not in x for y in to_filter)]

    contrasts = dictfilt(contrasts, beh_regs)

    if mnum=='model8':
        contrasts.update({'rewardedAttrFractalVsLottery':contrasts['rewardedAttrFractal_st'] - contrasts['rewardedAttrLottery_st'],
        'rewardedVsNotRewarded': contrasts['rewarded_st'] - contrasts['notRewarded_st']})

    if mnum in ['model9', 'model10', 'model11a', 'model11b', 'model12']:
        contrasts.update({'rewardedVsNotRewarded': contrasts['rewarded_st'] - contrasts['notRewarded_st']})

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

def get_events(subnum, runnum, mnum, data_path, behavior_path, regress_rt=0):

    # Read in fmri events
    fn = os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-%s_events.tsv' %(subnum, subnum, runnum))
    events = pd.read_csv(fn, sep='\t')

    # Read in behavioral data with modeled value and RPE estimates
    behavior = pd.read_csv(behavior_path)

    # Extract the correct subnum and runnum from behavioral data
    run_behavior = behavior.query('subnum == %d & session == %d'%(int(subnum), int(runnum)))

    # Demean columns that might be used for parametric regressors
    demean_cols = ['probFractalDraw', 'reward', 'leftFractalRpe', 'leftBundleValAdv','rightFractalRpe', 'rpeLeftRightSum','valChosen', 'valUnchosen', 'valChosenLottery', 'valUnchosenLottery', 'valChosenFractal', 'valUnchosenFractal', 'valBundleSum', 'valChosenMinusUnchosen', 'valSumTvpFrac', 'valSumTvwpFrac', 'valSumQvpFrac', 'valSumQvwpFrac']
    demean_cols = [i for i in demean_cols if i in run_behavior.columns]
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

        if reg == 'valBundleSum_par':
            if regress_rt:
                cond_valBundleSum_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valBundleSum_par['duration'] = mean_rt
            else:
                cond_valBundleSum_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valBundleSum_par['trial_type'] = 'valBundleSum_par'
            cond_valBundleSum_par['modulation'] = demean_df['valBundleSum'].reset_index(drop=True)

        if reg == 'valBundleSumEarly_par':
            cond_valBundleSumEarly_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valBundleSumEarly_par['duration'] = 1
            cond_valBundleSumEarly_par['trial_type'] = 'valBundleSumEarly_par'
            cond_valBundleSumEarly_par['modulation'] = demean_df['valBundleSum'].reset_index(drop=True)

        if reg == 'valChosenMinusUnchosen_par':
            if regress_rt:
                cond_valChosenMinusUnchosen_par = events.query('trial_type == "stimulus"')[['onset']].reset_index(drop=True)
                cond_valChosenMinusUnchosen_par['duration'] = mean_rt
            else:
                cond_valChosenMinusUnchosen_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenMinusUnchosen_par['trial_type'] = 'valChosenMinusUnchosen_par'
            cond_valChosenMinusUnchosen_par['modulation'] = demean_df['valChosenMinusUnchosen'].reset_index(drop=True)

        if reg == 'valChosenMinusUnchosenLate_par':
            cond_valChosenMinusUnchosenLate_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenMinusUnchosenLate_par['onset'] = cond_valChosenMinusUnchosenLate_par['onset'] + cond_valChosenMinusUnchosenLate_par['duration'] - 1
            cond_valChosenMinusUnchosenLate_par['duration'] = 1
            cond_valChosenMinusUnchosenLate_par['trial_type'] = 'valChosenMinusUnchosenLate_par'
            cond_valChosenMinusUnchosenLate_par['modulation'] = demean_df['valChosenMinusUnchosen'].reset_index(drop=True)

        if reg == 'valRelativeLeftBundle_par':
            cond_valRelativeLeftBundle_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valRelativeLeftBundle_par['trial_type'] = 'valRelativeLeftBundle_par'
            cond_valRelativeLeftBundle_par['modulation'] = demean_df['leftBundleValAdv'].reset_index(drop=True)

        if reg == 'valSumTvpFrac_par':
            cond_valSumTvpFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valSumTvpFrac_par['trial_type'] = 'valSumTvpFrac_par'
            cond_valSumTvpFrac_par['modulation'] = demean_df['valSumTvpFrac'].reset_index(drop=True)

        if reg == 'valSumTvwpFrac_par':
            cond_valSumTvwpFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valSumTvwpFrac_par['trial_type'] = 'valSumTvwpFrac_par'
            cond_valSumTvwpFrac_par['modulation'] = demean_df['valSumTvwpFrac'].reset_index(drop=True)

        if reg == 'valSumQvpFrac_par':
            cond_valSumQvpFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valSumQvpFrac_par['trial_type'] = 'valSumQvpFrac_par'
            cond_valSumQvpFrac_par['modulation'] = demean_df['valSumQvpFrac'].reset_index(drop=True)

        if reg == 'valSumQvwpFrac_par':
            cond_valSumQvwpFrac_par = events.query('trial_type == "stimulus"')[['onset', 'duration']].reset_index(drop=True)
            cond_valSumQvwpFrac_par['trial_type'] = 'valSumQvwpFrac_par'
            cond_valSumQvwpFrac_par['modulation'] = demean_df['valSumQvwpFrac'].reset_index(drop=True)

        if reg == 'valSumEarlyIntQv_par':
            cond_valSumEarlyIntQv_par = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_valSumEarlyIntQv_par['trial_type'] = 'valSumEarlyIntQv_par'
            cond_valSumEarlyIntQv_par['modulation'] = np.where(run_behavior['probFractalDraw']>0.5, run_behavior['leftQValue']+run_behavior['rightQValue'], 0)
            cond_valSumEarlyIntQv_par['modulation'] = cond_valSumEarlyIntQv_par['modulation'] - cond_valSumEarlyIntQv_par['modulation'].mean()

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

        if reg == 'rewardNotDemeaned_par':
            cond_rewardNotDemeaned_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardNotDemeaned_par['trial_type'] = 'rewardNotDemeaned_par'
            cond_rewardNotDemeaned_par['modulation'] = run_behavior['reward'].reset_index(drop=True)

        if reg == 'rewarded_par':
            rewardEvents = events.query('trial_type == "reward"').reset_index(drop=True)
            rewardedTrials = run_behavior.reset_index(drop=True).query("reward > 0").index
            rewardedEvents = rewardEvents.iloc[rewardedTrials,:]
            cond_rewarded_par = rewardedEvents[['onset', 'duration']].reset_index(drop=True)
            cond_rewarded_par['trial_type'] = 'rewarded_par'
            rewards = np.array(run_behavior.query("reward > 0")['reward'])
            cond_rewarded_par['modulation'] = rewards - rewards.mean()

        if reg == "rpeLeftFractal_par":
            cond_rpeLeftFractal_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeLeftFractal_par['trial_type'] = 'rpeLeftFractal_par'
            cond_rpeLeftFractal_par['modulation'] = demean_df['leftFractalRpe'].reset_index(drop=True)

        if reg == "rpeRightFractal_par":
            cond_rpeRightFractal_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeRightFractal_par['trial_type'] = 'rpeRightFractal_par'
            cond_rpeRightFractal_par['modulation'] = demean_df['rightFractalRpe'].reset_index(drop=True)

        if reg == 'rpeLeftRightSum_par':
            cond_rpeLeftRightSum_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeLeftRightSum_par['trial_type'] = 'rpeLeftRightSum_par'
            cond_rpeLeftRightSum_par['modulation'] = demean_df['rpeLeftRightSum'].reset_index(drop=True)

        # Same as above but when this reg is specified a different events file is read in as specified in level1.py
        if reg == 'rpeBestModelLeftRightSum_par':
            cond_rpeBestModelLeftRightSum_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeBestModelLeftRightSum_par['trial_type'] = 'rpeBestModelLeftRightSum_par'
            cond_rpeBestModelLeftRightSum_par['modulation'] = demean_df['rpeLeftRightSum'].reset_index(drop=True)

        if reg == 'rpeLeftRightSumEarly_par':
            cond_rpeLeftRightSumEarly_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeLeftRightSumEarly_par['duration'] = 1
            cond_rpeLeftRightSumEarly_par['trial_type'] = 'rpeLeftRightSumEarly_par'
            cond_rpeLeftRightSumEarly_par['modulation'] = demean_df['rpeLeftRightSum'].reset_index(drop=True)

        if reg == 'rpeLeftRightSumLate_par':
            cond_rpeLeftRightSumLate_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeLeftRightSumLate_par['onset'] = cond_rpeLeftRightSumLate_par['onset'] + cond_rpeLeftRightSumLate_par['duration'] - 1
            cond_rpeLeftRightSumLate_par['duration'] = 1
            cond_rpeLeftRightSumLate_par['trial_type'] = 'rpeLeftRightSumLate_par'
            cond_rpeLeftRightSumLate_par['modulation'] = demean_df['rpeLeftRightSum'].reset_index(drop=True)

        if reg == 'rpeRelativeLeftFractal_par':
            cond_rpeRelativeLeftFractal_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeRelativeLeftFractal_par['trial_type'] = 'rpeRelativeLeftFractal_par'
            cond_rpeRelativeLeftFractal_par['modulation'] = run_behavior['leftFractalRpe'] - run_behavior['rightFractalRpe']
            cond_rpeRelativeLeftFractal_par['modulation'] = cond_rpeRelativeLeftFractal_par['modulation'] - cond_rpeRelativeLeftFractal_par['modulation'].mean()

        if reg == 'rpeWeightedByRelevance_par':
            cond_rpeWeightedByRelevance_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeWeightedByRelevance_par['trial_type'] = 'rpeWeightedByRelevance_par'
            cond_rpeWeightedByRelevance_par['modulation'] = run_behavior['probFractalDraw']*run_behavior['rpeLeftRightSum']
            cond_rpeWeightedByRelevance_par['modulation'] = cond_rpeWeightedByRelevance_par['modulation'] - cond_rpeWeightedByRelevance_par['modulation'].mean()

        if reg == 'rpeWeightedByPerceivedRelevance_par':
            cond_rpeWeightedByPerceivedRelevance_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rpeWeightedByPerceivedRelevance_par['trial_type'] = 'rpeWeightedByPerceivedRelevance_par'
            cond_rpeWeightedByPerceivedRelevance_par['modulation'] = run_behavior['wpFrac']*run_behavior['rpeLeftRightSum']
            cond_rpeWeightedByPerceivedRelevance_par['modulation'] = cond_rpeWeightedByPerceivedRelevance_par['modulation'] - cond_rpeWeightedByPerceivedRelevance_par['modulation'].mean()

        if reg == 'rewardedAttrFractal_st':
            cond_rewardedAttrFractal_st = events.query('trial_type == "reward"')[['onset']].reset_index(drop=True)
            cond_rewardedAttrFractal_st['duration'] = 0
            cond_rewardedAttrFractal_st['trial_type'] = 'rewardedAttrFractal_st'
            cond_rewardedAttrFractal_st['modulation'] = run_behavior['fractalDraw']

        if reg == 'rewardedAttrLottery_st':
            cond_rewardedAttrLottery_st = events.query('trial_type == "reward"')[['onset']].reset_index(drop=True)
            cond_rewardedAttrLottery_st['duration'] = 0
            cond_rewardedAttrLottery_st['trial_type'] = 'rewardedAttrLottery_st'
            cond_rewardedAttrLottery_st['modulation'] = 1-run_behavior['fractalDraw']

        if reg == 'rewardedAttrSurprise_par':
            cond_rewardedAttrSurprise_par = events.query('trial_type == "reward"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardedAttrSurprise_par['trial_type'] = 'rewardedAttrSurprise_par'
            cond_rewardedAttrSurprise_par['modulation'] = np.where(run_behavior['fractalDraw'], 1-run_behavior['wpFrac'], run_behavior['wpFrac'])
            cond_rewardedAttrSurprise_par['modulation'] = cond_rewardedAttrSurprise_par['modulation']-cond_rewardedAttrSurprise_par['modulation'].mean()

        if reg == 'rewarded_st':
            cond_rewarded_st = events.query('trial_type == "reward"')[['onset']].reset_index(drop=True)
            cond_rewarded_st['duration'] = 0
            cond_rewarded_st['trial_type'] = 'rewarded_st'
            cond_rewarded_st['modulation'] = np.where(run_behavior['reward']>0, 1, 0)

        if reg == 'notRewarded_st':
            cond_notRewarded_st = events.query('trial_type == "reward"')[['onset']].reset_index(drop=True)
            cond_notRewarded_st['duration'] = 0
            cond_notRewarded_st['trial_type'] = 'notRewarded_st'
            cond_notRewarded_st['modulation'] = np.where(run_behavior['reward']==0, 1, 0)

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

# Fixed effects analysis for all runs of subjects based on tutorial on:
# https://nilearn.github.io/stable/auto_examples/04_glm_first_level/plot_fiac_analysis.html#sphx-glr-auto-examples-04-glm-first-level-plot-fiac-analysis-py
def run_level1(subnum, mnum, data_path, behavior_path, out_path, regress_rt=0, save_contrast = True, output_type='effect_size', noise_model='ar1', hrf_model='spm', drift_model='cosine',smoothing_fwhm=5):

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    contrasts_path = os.path.join(out_path, "sub-%s/contrasts"%(subnum))
    if not os.path.exists(contrasts_path):
        os.makedirs(contrasts_path)

    sub_events = glob.glob(os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-*_events.tsv'%(subnum, subnum)))
    sub_events.sort()

    #fmri_img: path to preproc_bold's that the model will be fit on
    fmri_img = glob.glob(os.path.join(data_path,"derivatives/fmriprep/sub-%s/func/sub-%s_task-bundles_run-*_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz"%(subnum, subnum)))
    fmri_img.sort()

    if len(fmri_img) == 0:
        print("***********************************************")
        print("No pre-processed BOLD found for sub-%s "%(subnum))
        print("***********************************************")
    else:
        if len(fmri_img) != 5:
            print("***********************************************")
            print("Found fewer than 5 runs for sub-%s "%(subnum))
            print("***********************************************")

        design_matrix = []
        for run_events in sub_events:
            runnum = re.findall('\d+', os.path.basename(run_events))[1] #index 0 is subnum, index 1 for runnum
            run_design_matrix = make_level1_design_matrix(subnum, runnum, mnum, data_path, behavior_path, regress_rt=regress_rt, hrf_model = hrf_model, drift_model=drift_model)
            #This subject has 817 instead of 892 scans in their last run. This leads to a lower cosine drift order and causes problems when calculating contrasts combined with other runs because the design matrix ends up with one less column compared to other runs'.
            if subnum == '02' and runnum == '5':
                run_design_matrix['drift_17'] = 0
            design_matrix.append(run_design_matrix)
            print("***********************************************")
            print("Saving design matrix for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            run_design_matrix.to_csv(os.path.join(out_path, 'sub-%s/sub-%s_run-%s_%s_reg-rt%s_level1_design_matrix.csv' %(subnum, subnum, runnum, mnum, str(regress_rt))), index=False)

        #define GLM parmeters
        img_tr = get_from_sidecar(subnum, '1', 'RepetitionTime', data_path) #get tr info from runnum = "1" since it's the same for all runs
        mask_img = nib.load(os.path.join(data_path,'derivatives/fmriprep/sub-%s/func/sub-%s_task-bundles_run-1_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'%(subnum, subnum))) #mask image from first run since it should be the same for all runs
        fmri_glm = FirstLevelModel(t_r=img_tr,
                               noise_model=noise_model,
                               hrf_model=hrf_model,
                               drift_model=drift_model,
                               smoothing_fwhm=smoothing_fwhm,
                               mask_img=mask_img,
                               subject_label=subnum,
                               minimize_memory=True)

        #fit glm to run image using run events
        print("***********************************************")
        print("Running fixed effects GLM for all runs of sub-%s"%(subnum))
        print("***********************************************")
        fmri_glm = fmri_glm.fit(fmri_img, design_matrices = design_matrix)

        print("***********************************************")
        print("Saving GLM for sub-%s"%(subnum))
        print("***********************************************")
        fn = os.path.join(out_path, 'sub-%s/sub-%s_%s_reg-rt%s_level1_glm.pkl' %(subnum, subnum, mnum, str(regress_rt)))
        f = open(fn, 'wb')
        pickle.dump(fmri_glm, f)
        f.close()

        # You don't need this step for group level analyses. You can load FirstLevelModel objects for SecondLevelModel.fit() inputs
        # But if you want to use images instead of FirstLevelModel objects as the input then `output_type` should be `effect_size` so you save the parameter maps and not other statistics
        if save_contrast:
            print("***********************************************")
            print("Running contrasts for sub-%s"%(subnum))
            print("***********************************************")
            contrasts = make_contrasts(design_matrix[0], mnum) #using the first design matrix since contrasts are the same for all runs
            for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
                contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= output_type)
                nib.save(contrast_map, '%s/sub-%s_%s_reg-rt%s_%s_%s.nii.gz'%(contrasts_path, subnum, mnum, str(regress_rt), contrast_id, output_type))
                contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= 'stat') #also save tmaps
                nib.save(contrast_map, '%s/sub-%s_%s_reg-rt%s_%s_%s.nii.gz'%(contrasts_path, subnum, mnum, str(regress_rt), contrast_id, 'tmap'))
            print("***********************************************")
            print("Done saving contrasts for sub-%s"%(subnum))
            print("***********************************************")
