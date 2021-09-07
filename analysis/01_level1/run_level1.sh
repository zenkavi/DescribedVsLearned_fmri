set -e
for modelnum in model1 model1a model2 model3 model4 model6 model5a model6 model6a model7 model8 model9 model10 model10a model11
do
  for subnum in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 27
  do
    for reg_rt in 0
    do
      sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SUBNUM}/$subnum/g" -e "s/{REG_RT}/$reg_rt/g" run_level1.batch | sbatch
    done
  done
done
