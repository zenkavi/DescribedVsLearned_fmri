**IMPORTANT**: If you're using zsh, which is the new default on Mac Terminals you need to include `noglob` before running the docker image so it interprets the `*` wildcards correctly.

Explore DICOM structures and specify the `heuristics` file.

```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration:/base nipy/heudiconv:latest \
-d /base/raw_fMRI_data/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-o /base/Nifti/ \
-f convertall \
-s 03 \
-c none --overwrite
```

On an EC2 instance

```
docker run --rm -it -v /home/ec2-user:/home nipy/heudiconv:latest \
-d /home/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-o /home/ \
-f convertall \
-s 01 \
-c none --overwrite
```

Get all subjects' ages from dicoms

```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration:/base nipy/heudiconv:latest \
-d /base/raw_fMRI_data/AR-GT-BUNDLES-{subject}_RANGEL/*/LOCALIZER_*/*.IMA \
-o /base/Nifti/ \
-f convertall \
-s 02 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 27 \
-c none --overwrite
```

Convert dicoms of subject 01 into BIDS on EC2

```
docker run --rm -it -v /home/ec2-user:/home nipy/heudiconv:latest \
-d /home/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-b -o /base/Nifti/ \
-f /home/heuristic.py \
-s 01 \
-c dcm2niix --overwrite
```
