set -e
for regname in cross crossRt fractalProb fractalProbParam stim stimRt valDiff choiceLeft conflict noconflict reward rewardParam rpe 
do
sed -e "s/{REGNAME}/$regname/g" run_level3.batch | sbatch
done
