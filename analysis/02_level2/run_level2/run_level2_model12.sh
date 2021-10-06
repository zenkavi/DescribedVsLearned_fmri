set -e
for modelnum in model12
do
  for modelname in overall-mean
  do
    for sign in pos neg
    do
      for tfce in 1
      do
        for regname in fractalProb_ev fractalProb_par stim_ev choiceShift_st valRelativeLeftBundle_par reward_ev reward_par rpeWhenFractalRewarded_par rewardedAttrSurprise_par rewarded_st notRewarded_st rewardedVsNotRewarded
        do
          for reg_rt in 0
          do
            for package in fsl
            do
              sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{MODELNAME}/$modelname/g" -e "s/{SIGN}/$sign/g" -e "s/{TFCE}/$tfce/g" -e "s/{REGNAME}/$regname/g" -e "s/{REG_RT}/$reg_rt/g" -e "s/{PACKAGE}/$package/g" run_level2.batch | sbatch
            done
          done
        done
      done
    done
  done
done
