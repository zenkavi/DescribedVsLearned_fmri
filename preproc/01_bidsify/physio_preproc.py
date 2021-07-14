#!/usr/bin/python3
import datetime
import json
import numpy as np
import os
from pathlib import Path

DATA_PATH='/Users/zeynepenkavi/Downloads/GTavares_2017_arbitration/'

subnums = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '23', '24', '25', '27']

runnum_vals = ['1', '2', '3', '4', '5']

log_type_dict = {'resp': 'breating', 'puls': 'cardiac', 'ext': 'trigger'}

for i, cur_sub in enumerate(subnums):

    files_path = os.path.join(DATA_PATH, 'raw_fmri_data/AR-GT-BUNDLES-%s_RANGEL/Physio'%cur_sub)
    file_names = os.listdir(files_path)

    # filter out files ending with .ecg
    file_names = [f for f in file_names if not f.endswith('.ecg')]

    # Sort by acquisition time
    file_names.sort()

    # Run number lookup dict based on log_start_times in file_names
    runnum_keys = [f.split("_")[3] for f in file_names]
    runnum_keys = list(set(runnum_keys))
    runnum_keys.sort()
    runnum_dict = dict(zip(runnum_keys, runnum_vals))

    for j, cur_file in enumerate(file_names):

        cur_run_key = cur_file.split("_")[3]
        cur_run = runnum_dict[cur_run_key]

        content = Path(os.path.join(files_path, cur_file)).read_text()

        lines = content.splitlines()

        line = lines.pop(0)

        if 'ext' in cur_file:
            values = [int(v) for v in line.split(" ")[25:-1]]
        else:
            values = [int(v) for v in line.split(" ")[20:-1]]

        # Within the vector of voltage values are “trigger” events from the scanner. These are entered as 5000 (for trigger on) and 5003 (for trigger off). These values need to be stripped out of the vector. There will occasionally be extra values at the end of the voltage vector as final values in the buffer will be written to the file after the logging is stopped. This can result in the vector length being slightly longer than would be predicted from the log start and stop times described below.
        ts = np.array([v for v in values if v < 5000])

        #LogStartMDHTime
        # Most relevant are the Log Start and Stop times for the MDH and MPCU. These log times indicate the time at which pulse-ox recording was started and stopped. That is, the first pulse-ox value in the first line of the data file was acquired at the LogStart time. The MPCU values provide time-stamps derived from the clock within the PMU recording system. The MDH values are time-stamps derived from the clock in the scanner, which is the same clock used to provide time-stamps for DICOM images. The MDH values are therefore preferred for synchronization of the DICOM images with the physiologic recording log.
        log_start_time = lines[-5]
        log_start_time = int(log_start_time.split(" ")[2])

        #sub-<cur_sub>_task-bundles_run-<cur_run>_bold.json -> time.AcquisitionTime[0]
        fn = os.path.join(DATA_PATH, 'bids_nifti_wface/sub-%s/func/sub-%s_task-bundles_run-%s_bold.json'%(cur_sub, cur_sub, cur_run))
        f = open(fn)
        run_sidecar = json.load(f)
        f.close()
        scan_start_time = run_sidecar["AcquisitionTime"]
        tmp = scan_start_time.split(":")
        hour = int(tmp[0]) * 60 * 60 * 1000
        min = int(tmp[1]) * 60 * 1000
        sec = int(tmp[2].split(".")[0]) * 1000
        msec = int(tmp[2].split(".")[1]) / 1000
        scan_start_time = hour + min + sec + msec
        rel_start_time = (log_start_time - scan_start_time)/1000

#OUTPUTS


#.resp
#'sub-%s_task-bundles_run-%s_recording-breathing_physio.tsv.gz'%(cur_sub, cur_run)
#sub-%s_task-bundles_run-%s_recording-breathing_physio.json'%(cur_sub, cur_run)
{
   "SamplingFrequency": 50.0,
   "StartTime": -22.345,
   "Columns": ["respiratory"]
}

#.puls
#sub-%s_task-bundles_run-%s_recording-cardiac_physio.tsv.gz'%(cur_sub, cur_run)
#sub-%s_task-bundles_run-%s_recording-cardiac_physio.json'%(cur_sub, cur_run)
{
   "SamplingFrequency": 50.0,
   "StartTime": -22.345,
   "Columns": ["cardiac"]
}

#.ext
#sub-%s_task-bundles_run-%s_recording-trigger_physio.tsv.gz'%(cur_sub, cur_run)
#sub-%s_task-bundles_run-%s_recording-trigger_physio.json'%(cur_sub, cur_run)
{
   "SamplingFrequency": 100.0,
   "StartTime": -22.345,
   "Columns": ["trigger"]
}
