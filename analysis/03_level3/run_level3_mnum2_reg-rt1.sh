set -e
for modelnum in model2
do
  for sign in pos neg
  do
    for tfce in 1
    do
      for regname in choiceRight_reg-rt1 choiceLeft_reg-rt1 conflict_reg-rt1 conflict-gt-noconflict_reg-rt1 cross_reg-rt1 fractalProb_reg-rt1 fractalProbParam_reg-rt1 noconflict_reg-rt1 reward_reg-rt1 rewardParam_reg-rt1 rpe_reg-rt1 stim_reg-rt1 task-on_reg-rt1  valChosen_reg-rt1 valUnchosen_reg-rt1
      do
        sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SIGN}/$sign/g" -e "s/{TFCE}/$tfce/g" -e "s/{REGNAME}/$regname/g" run_level3.batch | sbatch
      done
    done
  done
done
