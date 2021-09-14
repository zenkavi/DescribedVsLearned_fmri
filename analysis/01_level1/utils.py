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

    if mnum == 'model7a':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st','valDiff_par', 'rewardBin_ev', 'noRewardBin_ev', 'rewardLeftFractal_par', 'rewardRightFractal_par','rpeLeftFractal_par', 'rpeRightFractal_par', 'ppe_par']

    if mnum == 'model7b':
        regs = ['fractalProb_ev', 'fractalProb_par', 'stim_ev', 'choiceShift_st','valDiff_par', 'rewardBin_ev', 'noRewardBin_ev', 'rewardLeftFractal_ev', 'rewardRightFractal_ev','rpeLeftFractal_par', 'rpeRightFractal_par', 'ppe_par']

    return regs
