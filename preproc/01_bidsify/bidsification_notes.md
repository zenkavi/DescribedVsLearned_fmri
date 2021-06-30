
######################################
# Heudiconv
######################################
Convert DICOMs to Nifti in BIDS format  

**IMPORTANT**: If you're using zsh, which is the new default on Mac Terminals you need to include `noglob` before running the docker image so it interprets the `*` wildcards correctly.

- Explore DICOM structures and specify the `heuristics` file.
```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration:/base nipy/heudiconv:latest \
-d /base/raw_fMRI_data/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-o /base/ \
-f convertall \
-s 03 \
-c none --overwrite
```

- Get all subjects' ages from dicoms
```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration:/base nipy/heudiconv:latest \
-d /base/raw_fMRI_data/AR-GT-BUNDLES-{subject}_RANGEL/*/LOCALIZER_*/*.IMA \
-o /base/Nifti/ \
-f convertall \
-s 02 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 27 \
-c none --overwrite
```

- Convert dicoms of subject 01 into BIDS locally after copying single subject directory out to a temporary directory to avoid mounting the whole raw data directory. Check this then with the bidsvalidator on a browser to make sure the heuristics file is correct
```
noglob docker run --rm -it -v /Users/zeynepenkavi/Downloads/tmp:/base  \
-v /Users/zeynepenkavi/Downloads/GTavares_2017_arbitration/bids_nifti_wface:/out \
-v /Users/zeynepenkavi/Documents/RangelLab/DescribedVsLearned_fmri/preproc/01_bidsify:/code \
nipy/heudiconv:latest \
-d /base/AR-GT-BUNDLES-{subject}_RANGEL/*/*/*.IMA \
-b -o /out/ \
-f /code/heuristic.py \
-s 01 \
-c dcm2niix --overwrite
```

- How to run heudiconv parallel on cluster?

######################################
# Physio
######################################

######################################
# Event files
######################################

######################################
# bidsvalidator
######################################
