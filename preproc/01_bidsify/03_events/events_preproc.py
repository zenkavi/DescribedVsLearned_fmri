import os

DATA_PATH='/shared/behavioral_data'

file_names = os.listdir(DATA_PATH)

for i, cur_file in enumerate(file_names):
    cur_sub = ...
    cur_run = ...
    OUT_PATH='/shared/bids_nifti_wface/sub-%s/func/sub-%s_task-bundles_run-%s_events.tsv'%(cur_sub, cur_sub, cur_run)
