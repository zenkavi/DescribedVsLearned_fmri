set -e
for modelnum in model1
do
  for sign in pos neg
  do
    for tfce in 1 0
    do
      for regname in cross crossRt fractalProb fractalProbParam stim stimRt valDiff choiceLeft conflict noconflict reward rewardParam rpe
      do
        sed -e "s/{MODELNUM}/$modelnum/g" "s/{SIGN}/$sign/g" "s/{TFCE}/$tfce/g" "s/{REGNAME}/$regname/g" run_level3.batch | sbatch
      done
    done
  done
done
