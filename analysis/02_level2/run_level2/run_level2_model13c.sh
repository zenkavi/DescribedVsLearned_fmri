set -e
for modelnum in model13c
do
  for sign in pos neg
  do
    for regname in valSumQvpFrac_par
    do
      for package in nilearn
      do
        sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SIGN}/$sign/g" -e "s/{REGNAME}/$regname/g" -e "s/{PACKAGE}/$package/g" run_level2.batch | sbatch
      done
    done
  done
done
