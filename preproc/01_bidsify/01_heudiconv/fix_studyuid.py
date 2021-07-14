#!/usr/bin/python3

#go thru all dicoms and look for inconsistent studyUIDs, if there are any, change them to match the first one.
import pydicom
import glob

DATA_PATH = '/shared/raw_fmri_data/'

alldcm = glob.glob(DATA_PATH + '/*/*/*/*.IMA')
for jj in range(0,len(alldcm)):
    ds = pydicom.dcmread(alldcm[jj])
    if jj is 0:
        studyUID = ds.StudyInstanceUID
    ds.StudyInstanceUID= studyUID
    ds.save_as(alldcm[jj])
