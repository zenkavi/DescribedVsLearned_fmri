set -e
for modelnum in model1 model1a model2 model3
do
  for modelname in overall-mean
  do
    for sign in pos neg
    do
      for tfce in 1
      do
        for regname in stim_rt
        do
          for reg_rt in 1
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
