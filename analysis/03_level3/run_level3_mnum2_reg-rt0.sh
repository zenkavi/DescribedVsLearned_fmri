set -e
for modelnum in model2
do
  for sign in pos neg
  do
    for tfce in 1
    do
      for regname in choiceRight_reg-rt0 choiceLeft_reg-rt0 conflict_reg-rt0 conflict-gt-noconflict_reg-rt0 cross_reg-rt0 fractalProb_reg-rt0 fractalProbParam_reg-rt0 noconflict_reg-rt0 reward_reg-rt0 rewardParam_reg-rt0 rpe_reg-rt0 stim_reg-rt0 task-on_reg-rt0  valChosen_reg-rt0 valUnchosen_reg-rt0
      do
        sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SIGN}/$sign/g" -e "s/{TFCE}/$tfce/g" -e "s/{REGNAME}/$regname/g" run_level3.batch | sbatch
      done
    done
  done
done
