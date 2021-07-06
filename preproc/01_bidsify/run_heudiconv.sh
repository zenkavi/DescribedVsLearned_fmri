set -e
for subnum in 01 02
do
sed -e "s/{SUBNUM}/$subnum/g" run_heudiconv.batch | sbatch
done
