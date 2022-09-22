set -e
for modelnum in model13a model13b model13c model13d
do
  for subnum in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 27
  do
    sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SUBNUM}/$subnum/g" run_level1.batch | sbatch
  done
done
