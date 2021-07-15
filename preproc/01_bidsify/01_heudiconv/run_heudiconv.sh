set -e
for subnum in 07 08 09 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25
do
sed -e "s/{SUBNUM}/$subnum/g" run_heudiconv.batch | sbatch
done
