set -e
for modelnum in model1
do
  for regname in cross crossRt fractalProb fractalProbParam stim stimRt valDiff choiceLeft conflict noconflict reward rewardParam rpe
  do
    sed -e "s/{MODELNUM}/$modelnum/g" "s/{REGNAME}/$regname/g" run_level3.batch | sbatch
  done
done
