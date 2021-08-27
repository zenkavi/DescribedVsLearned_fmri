set -e
for modelnum in model1
do
  for modelname in overall-mean group-diff group-means
  do
    for sign in pos neg
    do
      for tfce in 1
      do
        for regname in cross_ev fractalProb_ev stim_ev choice_st reward_ev
        do
          for reg_rt in 0 1
          do
            sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{MODELNAME}/$modelname/g" -e "s/{SIGN}/$sign/g" -e "s/{TFCE}/$tfce/g" -e "s/{REGNAME}/$regname/g" -e "s/{REG_RT}/$reg_rt/g" run_level3.batch | sbatch
          done
        done
      done
    done
  done
done
