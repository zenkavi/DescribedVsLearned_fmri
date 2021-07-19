import os
from scipy.io import loadmat
import pandas as pd

DATA_PATH='/shared/behavioral_data'

file_names = os.listdir(DATA_PATH)
file_names.sort()

for i, cur_file in enumerate(file_names):
    tmp = cur_file.split("-")[3]
    cur_sub = tmp.split("_")[0]
    cur_run = tmp.split("_")[1][-1]

    cur_data = loadmat(os.path.join(DATA_PATH, cur_file))

    onsetCross = cur_data['data']['onsetCross'][0][0]
    onsetProbabilities = cur_data['data']['onsetProbabilities'][0][0]
    onsetStimulus = cur_data['data']['onsetStimulus'][0][0]
    onsetReward = cur_data['data']['onsetReward'][0][0]
    reactionTime = cur_data['data']['reactionTime'][0][0]

    onsets = np.concatenate((onsetCross, onsetProbabilities, onsetStimulus, onsetReward), axis=None)

    numTrials = len(onsetCross[0])
    trialTypes = np.concatenate((np.repeat(['cross'], numTrials), np.repeat(['fractalProb'], numTrials), np.repeat(['stimulus'], numTrials), np.repeat(['reward'], numTrials)), axis=None)

    cur_events = pd.DataFrame(data = {'onset': onsets, 'duration': durations, 'trial_type': trialTypes, 'response_time': ..., 'stim_file'})
    cur_events = cur_events.sort_values(by=['onset'])

    OUT_PATH='/shared/bids_nifti_wface/sub-%s/func/sub-%s_task-bundles_run-%s_events.tsv'%(cur_sub, cur_sub, cur_run)
