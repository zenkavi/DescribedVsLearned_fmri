set -e
for subnum in 04 05
do
  for reg_rt in 0 1
  do
    sed -e "s/{SUBNUM}/$subnum/g" "s/{REG_RT}/$reg_rt/g" run_level1.batch | sbatch
  done
done
