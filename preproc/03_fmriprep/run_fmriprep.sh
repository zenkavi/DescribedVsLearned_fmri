set -e
for subnum in 04 05
do
sed -e "s/{SUBNUM}/$subnum/g" run_fmriprep.batch | sbatch
done
