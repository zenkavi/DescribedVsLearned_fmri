import json
import os
import numpy as np
import pandas as pd
from scipy.io import loadmat


DATA_PATH='/shared/behavioral_data'

file_names = os.listdir(DATA_PATH)
file_names.sort()

sidecar = {
  "onset": {
    "Description": "Onset (in seconds) of the event measured from the beginning of the acquisition of the first volume."
  },
  "duration": {
    "Description": "Duration of the event (measured from onset) in seconds."
  },
  "trial_type": {
    "LongName": "Event category",
    "Description": "Indicator of the phase of each trial",
    "Levels": {
      "cross": "Fixation cross",
      "fractalProb": "Presentation of the probabilities trial reward might come from a fractal or lottery draw",
      "stimulus": "Presentation of all fractals and all lotteries for the trial",
      "reward": "Presentation of the trial reward"
    }
  },
  "response_time": {
    "Description": "Amount of time in seconds it took subjects to make a decision between the bundles of lotteries and fractals"
  },
  "identifier": {
    "Description": "Path to fractals used for the session. Fractal images can be found in root directory."
  },
  "StimulusPresentation": {
    "SoftwareName": "Psychtoolbox",
    "SoftwareRRID": "SCR_002881",
    "SoftwareVersion": "3.0.11",
    "Code": "doi:10.5281/zenodo.3361717"
    }
}

for i, cur_file in enumerate(file_names):

    # Parse file name
    tmp = cur_file.split("-")[3]
    cur_sub = tmp.split("_")[0]
    cur_run = tmp.split("_")[1][-1]

    # Read in behavioral data
    cur_data = loadmat(os.path.join(DATA_PATH, cur_file))

    # Extract needed bits from behavioral data
    onsetCross = cur_data['data']['onsetCross'][0][0][0]
    onsetProbabilities = cur_data['data']['onsetProbabilities'][0][0][0]
    onsetStimulus = cur_data['data']['onsetStimulus'][0][0][0]
    onsetReward = cur_data['data']['onsetReward'][0][0][0]
    reactionTime = cur_data['data']['reactionTime'][0][0][0]
    leftFractal = str(cur_data['data']['fractals'][0][0][0][0])
    rightFractal = str(cur_data['data']['fractals'][0][0][1][0])

    # Make columns of the events file

    # Onset column
    onsets = np.concatenate((onsetCross, onsetProbabilities, onsetStimulus, onsetReward), axis=None)

    # Duration column
    durationCross = onsetProbabilities - onsetCross
    durationProbabilities = onsetStimulus - onsetProbabilities
    durationStimulus = reactionTime
    durationReward = np.concatenate((onsetCross[1:]-onsetReward[:-1], [3.]), axis=None) #Appending 3 for last trials of the run
    durations = np.concatenate((durationCross, durationProbabilities, durationStimulus, durationReward), axis=None)

    # Trial_type column
    numTrials = len(onsetCross)
    trialTypes = np.concatenate((np.repeat(['cross'], numTrials), np.repeat(['fractalProb'], numTrials), np.repeat(['stimulus'], numTrials), np.repeat(['reward'], numTrials)), axis=None)

    # Response_time column
    response_times = np.concatenate(np.repeat([reactionTime], 4, axis=0))

    # Identifier column. Not using Stim_file column bc bidsvalidator doesn't accept paths to two images
    identifiers = np.repeat(['images/%s.jpg, images/%s.jpg'%(leftFractal, rightFractal)], len(trialTypes))

    # Put everything together for the events file
    cur_events = pd.DataFrame(data = {'onset': onsets, 'duration': durations, 'trial_type': trialTypes, 'response_time': response_times, 'identifier': identifiers})
    cur_events = cur_events.sort_values(by=['onset'])

    # Create output path if needed
    OUT_PATH='/shared/bids_nifti_wface/sub-%s/func/'%(cur_sub)
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)

    # Write events output
    fn = os.path.join(OUT_PATH, 'sub-%s_task-bundles_run-%s_events.tsv'%(cur_sub, cur_run))
    cur_events.to_csv(fn, sep='\t',index=False)

    # Write sidecar
    fn = os.path.join(OUT_PATH, 'sub-%s_task-bundles_run-%s_events.json'%(cur_sub, cur_run))
    with open(fn, 'w') as f:
        json.dump(sidecar, f)
