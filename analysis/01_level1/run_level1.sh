set -e
for subnum in 10 11 15 16 17 20 22 23 24 25 27
do
  for reg_rt in 0 1
  do
    sed -e "s/{SUBNUM}/$subnum/g" -e "s/{REG_RT}/$reg_rt/g" run_level1.batch | sbatch
  done
done
