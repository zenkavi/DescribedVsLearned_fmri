set -e
for subnum in 03 04
do
sed -e "s/{SUBNUM}/$subnum/g" run_fmriprep.batch | sbatch
done
