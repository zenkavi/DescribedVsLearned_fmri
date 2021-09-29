import numpy as np
import nibabel as nib
import os
from nilearn.plotting import plot_stat_map, view_img
import pandas as pd
from nilearn.glm.first_level import make_first_level_design_matrix, spm_hrf

def get_img_path(reg, reg_rt="0", mnum = "1", mname = "overall-mean"):
    level2_path = '/Users/zeynepenkavi/Downloads/GTavares_2017_arbitration/bids_nifti_wface/derivatives/nilearn/glm/level2/'
    model_path = 'model'+mnum+'_reg-rt'+reg_rt
    img_path = os.path.join(level2_path, model_path, mname, reg+'_'+model_path)
    
    return img_path

def get_filt_tval_img(reg, reg_rt = "0", mnum = "1", mname = 'overall-mean', tstat="1", threshold=0.95, nofilt=False):
    
    img_path = get_img_path(reg=reg, reg_rt=reg_rt, mnum=mnum, mname=mname)
    
    tval_fn = '%s_model%s_reg-rt%s_pos_%s_randomise_tstat%s.nii.gz'%(reg, mnum, reg_rt, mname, tstat)
    
    tval_img = os.path.join(img_path, tval_fn)
    
    tval_img = nib.load(tval_img)
    
    tval_data = tval_img.get_fdata()
    
    if nofilt:
        filt_tval_img = tval_img
    else:
        pos_pval_fn = '%s_model%s_reg-rt%s_pos_%s_randomise_tfce_corrp_tstat%s.nii.gz'%(reg, mnum, reg_rt, mname, tstat)
        neg_pval_fn = '%s_model%s_reg-rt%s_neg_%s_randomise_tfce_corrp_tstat%s.nii.gz'%(reg, mnum, reg_rt, mname, tstat)
        
        pos_pval_img = os.path.join(img_path, pos_pval_fn)
        neg_pval_img = os.path.join(img_path, neg_pval_fn)
        
        pos_pval_img = nib.load(pos_pval_img)
        neg_pval_img = nib.load(neg_pval_img)
        
        pos_pval_data = pos_pval_img.get_fdata()
        neg_pval_data = neg_pval_img.get_fdata()
        
        filt_tval_data = np.where(pos_pval_data > threshold, tval_data, np.where(neg_pval_data > threshold, tval_data, 0))
        filt_tval_img = nib.Nifti1Image(filt_tval_data.astype(np.float64), tval_img.affine)
    
    return filt_tval_img

def plot_filt_tval_img(reg, reg_rt = "0", mnum = "1", mname = 'overall-mean', tstat="1", threshold=0.95, interactive=False, cut_coords = None, display_mode = 'ortho', draw_cross=False, title=None, nofilt=False, t_threshold=None):
    filt_tval_img = get_filt_tval_img(reg=reg, reg_rt = reg_rt, mnum = mnum, mname = mname, tstat=tstat, threshold=threshold, nofilt=nofilt)
    
    if title is None:
        title='%s_model%s_reg-rt%s'%(reg, mnum, reg_rt)
    
    if nofilt:
        plot_threshold=t_threshold
    else:
        plot_threshold=1e-06
    
    if(len(np.unique(filt_tval_img.get_fdata())) == 1):
        print('Nothing survives correction for %s, model = %s, tstat = %s, reg_rt = %s at threshold p < %s'%(reg, mnum, tstat, reg_rt, str(round(1-threshold, 2))))
    elif interactive:
        view = view_img(filt_tval_img, 
             draw_cross=draw_cross,
             title=title, cut_coords = cut_coords, threshold=plot_threshold)
        
        return view
    else:
        print('Plotting tvalues filtered for corrected p values < %s'%str(round(1-threshold, 2)))
        plot_stat_map(filt_tval_img, 
             draw_cross=draw_cross,
             title=title, cut_coords = cut_coords, display_mode = display_mode, threshold=plot_threshold)

        
def get_filt_diff_tval_img(reg,  mnum1, mnum2, reg_rt1="0", reg_rt2="0", reg2=None, mname="overall-mean", tstat="1", threshold=0.95):
    
    if reg2 is None:
        reg2 = reg
    
    img1 = get_filt_tval_img(reg=reg, reg_rt = reg_rt1, mnum = mnum1, mname = mname, tstat=tstat, threshold=threshold)
    img2 = get_filt_tval_img(reg=reg2, reg_rt = reg_rt2, mnum = mnum2, mname = mname, tstat=tstat, threshold=threshold)
    
    img1_data = img1.get_fdata()
    img2_data = img2.get_fdata()
    filt_diff_tval_data = img1_data - img2_data
    filt_diff_tval_img = nib.Nifti1Image(filt_diff_tval_data.astype(np.float64), img1.affine)
    
    return filt_diff_tval_img
        
def plot_filt_diff_tval_img(reg, mnum1, mnum2, reg_rt1="0", reg_rt2="0",reg2 = None, mname = 'overall-mean', tstat="1", threshold=0.95, disp_threshold = 2, interactive=False, cut_coords = None, display_mode = 'ortho', draw_cross=False, title=None):
    filt_diff_tval_img = get_filt_diff_tval_img(reg=reg, reg_rt1 = reg_rt1, reg_rt2 = reg_rt2, mnum1 = mnum1, mnum2 = mnum2, reg2 = reg2, mname = mname, tstat=tstat, threshold=threshold)
    if title is None:
        title='%s model%s_reg-rt%s - model%s_reg-rt%s '%(reg, mnum1, reg_rt1, mnum2, reg_rt2)
    
    if(len(np.unique(filt_diff_tval_img.get_fdata())) == 1):
        print('Nothing survives correction for the difference image %s, model = %s, tstat = %s at threshold p < %s'%(reg, mnum, tstat, str(round(1-threshold, 2))))
    
    elif interactive:
        view = view_img(filt_diff_tval_img, 
             draw_cross=draw_cross,
             title=title, cut_coords = cut_coords, threshold = disp_threshold)
        
        return view
    else:
        print('Plotting tvalues filtered for corrected p values < %s'%str(round(1-threshold, 2)))
        plot_stat_map(filt_diff_tval_img, 
             draw_cross=draw_cross,
             title=title, cut_coords = cut_coords, display_mode = display_mode, threshold = disp_threshold)

        
def get_mean_cor_df(reg_rt = "0", mnum = "1"):
    
    level3_path = '/Users/zeynepenkavi/Downloads/GTavares_2017_arbitration/bids_nifti_wface/derivatives/nilearn/glm/level3/'
    model_path = 'model'+mnum+'_reg-rt'+reg_rt
    df_path = os.path.join(level3_path, model_path, model_path+'_mean_desmat_cor.csv')
    
    mean_cor_df = pd.read_csv(df_path)
    
    return(mean_cor_df)

def events_to_timeseries(frame_times, events, label = 'stim', hrf_model = 'spm'):
    
    if hrf_model is not None:
        events['trial_type']=label
    
    # Note I'm not making a design matrix per se here. Just using the function as convenience to make the timeseries from onsets, durations and amplitudes
    ts = make_first_level_design_matrix(frame_times, events, drift_model=None, hrf_model = hrf_model)
    ts['label'] = label
    ts = ts.rename(columns={label:'amplitude'})
    ts = ts[['label', 'amplitude']]
    ts['time'] = ts.index
    
    return ts

def get_b_est(dv, des_mat, roundto=3, intercept=True):
    if not isinstance(dv, np.ndarray):
        dv = dv['amplitude']
    if not intercept:
        des_mat = des_mat.drop(columns='constant')
    des_mat = des_mat.values
    b_est = np.linalg.inv(des_mat.T.dot(des_mat)).dot(des_mat.T).dot(dv)
    b_est = np.round(b_est, roundto)
    return b_est