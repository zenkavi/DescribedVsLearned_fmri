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

def get_conditions(cur_events, runnum, mean_rt, sub_pes, pe, sub_evs, ev):
    #process events for GLM
    #events: 4 col events file for WHOLE RUN with onset, duration, trial_type, modulation
    #trial_type column:
        #m1, m2, m3, m4 - onset: stimulus_presentation onset, duration: mean_rt, modulation: 1
        #m1_rt, m2_rt, m3_rt, m4_rt - onset: stimulus_presentation, duration: mean_rt, modulation: rt-mean_rt
        #gain - onset: response onset, duration: response duration, modulation: gain-mean_gain
        #loss - onset: reponse onset, duration: response duration, modulation: loss-mean_loss
        #junk: onset: response onset, duration: response duration, modulation: 1

    cur_events.response_time = cur_events.response_time/1000
    rt = cur_events.response_time
    cur_events.loc[:,'response_time'] = rt - rt[rt>0].mean()
    cur_events['rt_shift'] = cur_events.response_time.shift(-1)
    

    cond_m1 = cur_events.query('trial_type == "stim_presentation" & stimulus == 1')[['onset']]
    cond_m1['duration'] = mean_rt
    cond_m1['modulation'] = 1
    cond_m1['trial_type'] = 'm1'
    
    cond_ev = cur_events.query('trial_type == "stim_presentation"')
    cond_ev = pd.concat([cond_ev.reset_index(drop=True), run_evs['EV'].reset_index(drop=True)], axis=1)
    cond_m1_ev = cond_ev.query('trial_type == "stim_presentation" & stimulus == 1')
    
    
    #Demeaning for parametric regressors
    cond_m1_ev['EV'] = cond_m1_ev['EV'].sub(cond_m1_ev['EV'].mean())
    
    cond_m1_ev = cond_m1_ev[['onset', 'duration', 'EV']]
    cond_m1_ev = cond_m1_ev.rename(index=str, columns={"EV": "modulation"})
    cond_m1_ev['trial_type'] = 'm1_ev'
    
    cond_m1_rt = cur_events.query('trial_type == "stim_presentation" & stimulus == 1')[['onset', 'rt_shift']]
    cond_m1_rt['duration'] = mean_rt
    cond_m1_rt['modulation'] = cond_m1_rt['rt_shift']
    cond_m1_rt = cond_m1_rt.drop(['rt_shift'], axis=1)
    cond_m1_rt['trial_type'] = "m1_rt"
    
    cond_gain = cur_events.query('points_earned>0')[['onset', 'duration','points_earned']]
    cond_gain = cond_gain.rename(index=str, columns={"points_earned": "modulation"})
    cond_gain['trial_type'] =  "gain"
    
    cond_junk = cur_events.query('response == 0')[['onset', 'duration']]
    cond_junk['modulation'] = 1
    cond_junk['trial_type'] = "junk"

    formatted_events = pd.concat([cond_m1, cond_m2, cond_m3, cond_m4, cond_m1_rt, cond_m2_rt, cond_m3_rt, cond_m4_rt, cond_gain, cond_loss, cond_junk], ignore_index=True)

    formatted_events = formatted_events.sort_values(by='onset')

    formatted_events = formatted_events[['onset', 'duration', 'trial_type', 'modulation']].reset_index(drop=True)

    return formatted_events

def get_confounds(confounds, scrub_thresh = .5):
    
    confound_cols = [x for x in confounds.columns if 'trans' in x]+[x for x in confounds.columns if 'rot' in x]+['std_dvars', 'framewise_displacement']
    
    formatted_confounds = confounds[confound_cols]
    
    formatted_confounds = formatted_confounds.fillna(0)
    
    formatted_confounds['scrub'] = np.where(formatted_confounds.framewise_displacement>scrub_thresh,1,0)
    
    formatted_confounds = formatted_confounds.assign(
        scrub = lambda dataframe: dataframe['framewise_displacement'].map(lambda framewise_displacement: 1 if framewise_displacement > scrub_thresh else 0))
    
    return formatted_confounds

def run_level1(subnum, out_path, pe, pe_path, ev, ev_path, beta):

    data_loc = os.environ['DATA_LOC']
    events_files = glob.glob('%s/sub-*/func/sub-*_task-machinegame_run-*_events.tsv'%(data_loc))
    events_files.sort()

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    contrasts_path = "%s/contrasts"%(out_path)
    if not os.path.exists(contrasts_path):
        os.makedirs(contrasts_path)

    
    mean_rt = ...

    sub_events = [x for x in events_files if subnum in x]

    if pe:
        all_pes = pd.read_csv(pe_path)
        sub_pes = all_pes.query('sub_id == @subnum')
        del all_pes
    else:
        sub_pe = None

    if ev:
        all_evs = pd.read_csv(ev_path)
        sub_evs = all_evs.query('sub_id == @subnum')
        del all_evs
    else:
        sub_evs = None

    for run_events in sub_events:

        runnum = re.findall('\d+', os.path.basename(run_events))[1]

        exists = os.path.isfile(os.path.join(data_loc,"derivatives/fmriprep_1.4.0/fmriprep/sub-%s/func/sub-%s_task-machinegame_run-%s_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"%(subnum, subnum, runnum)))

        if exists:

            #fmri_img: path to preproc_bold that the model will be fit on
            fmri_img = os.path.join(data_loc,"derivatives/fmriprep_1.4.0/fmriprep/sub-%s/func/sub-%s_task-machinegame_run-%s_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"%(subnum, subnum, runnum))

            #read in preproc_bold for that run
            cur_img = nib.load(fmri_img)
            cur_img_tr = cur_img.header['pixdim'][4]

            #read in events.tsv for that run
            cur_events = pd.read_csv(run_events, sep = '\t')
            formatted_events = get_conditions(cur_events, runnum, mean_rt, sub_pes, pe, sub_evs, ev)

            #process confounds
            #['X','Y','Z','RotX','RotY','RotY','<-firsttemporalderivative','stdDVARs','FD','scrub']
            cur_confounds = pd.read_csv(os.path.join(data_loc,"derivatives/fmriprep_1.4.0/fmriprep/sub-%s/func/sub-%s_task-machinegame_run-%s_desc-confounds_regressors.tsv"%(subnum, subnum, runnum)), sep='\t')
            formatted_confounds = get_confounds(cur_confounds)

            #define GLM parmeters
            fmri_glm = FirstLevelModel(t_r=cur_img_tr,
                                   noise_model='ar1',
                                   standardize=False,
                                   hrf_model='spm + derivative',
                                   drift_model='cosine',
                                   smoothing_fwhm=5,
                                   mask='%s/derivatives/fmriprep_1.4.0/fmriprep/sub-%s/func/sub-%s_task-machinegame_run-%s_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'%(data_loc, subnum, subnum, runnum))

            #fit glm to run image using run events
            print("***********************************************")
            print("Running GLM for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            fmri_glm = fmri_glm.fit(fmri_img, events = formatted_events, confounds = formatted_confounds)

            print("***********************************************")
            print("Saving GLM for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            f = open('%s/sub-%s_run-%s_l1_glm.pkl' %(out_path,subnum, runnum), 'wb')
            pickle.dump(fmri_glm, f)
            f.close()

            #Save design matrix
            design_matrix = fmri_glm.design_matrices_[0]
            print("***********************************************")
            print("Saving design matrix for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            design_matrix.to_csv(os.path.join(out_path, 'sub-%s_run-%s_level1_design_matrix.csv' %(subnum, runnum)))

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