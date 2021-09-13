set -e
for modelnum in model7a
do
  for modelname in overall-mean
  do
    for sign in pos neg
    do
      for tfce in 1
      do
        for regname in fractalProb_ev fractalProb_par stim_ev choiceShift_st valDiff_par rewardBin_ev noRewardBin_ev rewardLeftFractal_par rewardRightFractal_par rpeLeftFractal_par rpeRightFractal_par ppe_par
        do
          for reg_rt in 0
          do
            sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{MODELNAME}/$modelname/g" -e "s/{SIGN}/$sign/g" -e "s/{TFCE}/$tfce/g" -e "s/{REGNAME}/$regname/g" -e "s/{REG_RT}/$reg_rt/g" run_level3.batch | sbatch
          done
        done
      done
    done
  done
done
