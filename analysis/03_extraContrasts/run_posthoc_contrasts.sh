set -e
for modelnum in model7a
do
  for modelname in overall-mean
  do
    for sign in pos neg
    do
      for tfce in 1
      do
        for regname in rewardBin_ev-vs-noRewardBin_ev
        do
          for reg_rt in 0
          do
            sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{MODELNAME}/$modelname/g" -e "s/{SIGN}/$sign/g" -e "s/{TFCE}/$tfce/g" -e "s/{REGNAME}/$regname/g" -e "s/{REG_RT}/$reg_rt/g" run_posthoc_contrasts.batch | sbatch
          done
        done
      done
    done
  done
done
