set -e
for modelnum in model1
do
  for sign in pos neg
  do
    for tfce in 1
    do
      for contrast in conflict_vs_noconflict
      do
        sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SIGN}/$sign/g" -e "s/{TFCE}/$tfce/g" -e "s/{CONTRAST}/$contrast/g" run_posthoc_contrasts.batch | sbatch
      done
    done
  done
done
