import os
import json

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

# For level 2, check_output (and posthoc contrasts?)
def get_model_regs_with_contrasts(mnum):

    regs = get_model_regs(mnum)

    if mnum == 'model8':
        regs.append('rewardedAttrFractalVsLottery')
        regs.append('rewardedVsNotRewarded')

    if mnum in ['model9', 'model10', 'model11a', 'model11b', 'model12', 'model13']:
        regs.append('rewardedVsNotRewarded')

    return regs

def get_model_regs(mnum):
    if mnum == 'model1':
        regs = ['fractalProb_ev', 'stim_ev', 'choiceShift_st', 'reward_ev']

    if mnum == 'model1a':
        regs = ['fractalProb_ev', 'stim_ev', 'choiceShiftLeft_st', 'choiceShiftRight_st', 'reward_ev']

    if mnum == 'model2':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev','choiceShift_st', 'reward_ev']

    if mnum == 'model3':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'valChosenMinusUnchosen_par', 'reward_ev', 'reward_par', 'rpeLeftRightSum_par']

    if mnum == 'model4':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'valChosenMinusUnchosenLate_par', 'reward_ev', 'reward_par', 'rpeLeftRightSumEarly_par']

    if mnum == 'model5':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'valChosenMinusUnchosenLate_par', 'reward_ev', 'reward_par', 'rpeLeftRightSumLate_par']

    if mnum == 'model6':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'valChosenMinusUnchosen_par', 'reward_ev', 'rpeLeftRightSum_par']

    if mnum == 'model7':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'valChosenMinusUnchosen_par', 'reward_ev', 'reward_par', 'rpeLeftFractal_par']

    if mnum == 'model8':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'valChosenMinusUnchosen_par', 'reward_ev', 'reward_par', 'rpeLeftRightSum_par', 'rewardedAttrFractal_st', 'rewardedAttrLottery_st', 'rewardedAttrSurprise_par', 'rewarded_st', 'notRewarded_st']

    if mnum == 'model9':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSumEarly_par', 'valChosenMinusUnchosenLate_par', 'reward_ev', 'reward_par', 'rpeLeftRightSumEarly_par', 'rewardedAttrSurprise_par', 'rewarded_st', 'notRewarded_st']

    if mnum == 'model10':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valRelativeLeftBundle_par', 'reward_ev', 'reward_par', 'rpeRelativeLeftFractal_par', 'rewardedAttrSurprise_par', 'rewarded_st', 'notRewarded_st']

    if mnum == 'model11a':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'reward_ev', 'reward_par', 'rpeWeightedByRelevance_par', 'rewardedAttrSurprise_par', 'rewarded_st', 'notRewarded_st']

    if mnum == 'model11b':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'reward_ev', 'reward_par', 'rpeWeightedByPerceivedRelevance_par', 'rewardedAttrSurprise_par', 'rewarded_st', 'notRewarded_st']

    if mnum == 'model12':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'reward_ev', 'reward_par', 'rpeWhenFractalRewarded_par', 'rewardedAttrSurprise_par', 'rewarded_st', 'notRewarded_st']

    if mnum == 'model13':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st', 'valBundleSum_par', 'reward_ev', 'reward_par', 'rpeChosenBundleFractal_par', 'rewardedAttrSurprise_par', 'rewarded_st', 'notRewarded_st']

    return regs
