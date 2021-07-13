#!/usr/bin/python3

import fmri_physio_log as fpl
import numpy as np
import os
from pathlib import Path

DATA_PATH='/Users/zeynepenkavi/Downloads/GTavares_2017_arbitration/'

subnums = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '23', '24', '25', '27']

runnum_vals = ['01', '02', '03', '04', '05']

rec_type_dict = {...}

for i, cur_sub in enumerate(subnums):

    files_path = os.path.join(DATA_PATH, 'raw_fmri_data/AR-GT-BUNDLES-%s_RANGEL/Physio'%cur_sub)
    file_names = os.listdir(files_path)

    # filter out files ending with .ecg
    file_names = [f for f in file_names if not f.endswith('.ecg')]

    # Sort by acquisition time
    file_names.sort()

    runnum_keys = [f.split("_")[3] for f in file_names]
    runnum_keys = list(set(runnum_keys))
    runnum_keys.sort()

    runnum_dict = dict(zip(runnum_keys, runnum_vals))

    for j, cur_file in enumerate(file_names):
        

        content = Path(os.path.join(files_path, cur_file)).read_text()

        lines = content.splitlines()

        line = lines.pop(0)

        if 'ext' in cur_file:
            values = [int(v) for v in line.split(" ")[25:-1]]
        else:
            values = [int(v) for v in line.split(" ")[20:-1]]

        ts = np.array([v for v in values if v < 5000])



#OUTPUTS
sub-01_task-bundles_run-1_bold.json -> time.AcquisitionTime[0]
#.resp
#sub-<label>_task-bundles_run-1_recording-breathing_physio.tsv.gz
#sub-<label>_task-bundles_run-1_recording-breathing_physio.json
{
   "SamplingFrequency": 50.0,
   "StartTime": -22.345,
   "Columns": ["respiratory"]
}

#.puls
#sub-<label>_task-bundles_run-1_recording-pulse_physio.tsv.gz
#sub-<label>_task-bundles_run-1_recording-pulse_physio.json
{
   "SamplingFrequency": 50.0,
   "StartTime": -22.345,
   "Columns": ["cardiac"]
}

#.ext
#sub-<label>_task-bundles_run-1_recording-trigger_physio.tsv.gz
#sub-<label>_task-bundles_run-1_recording-trigger_physio.json
{
   "SamplingFrequency": 100.0,
   "StartTime": -22.345,
   "Columns": ["trigger"]
}
