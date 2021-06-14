
- Transfer data to S3
  - One subject
  ```
  aws s3 sync AR-GT-BUNDLES-02_RANGEL s3://described-vs-experienced/raw_fmri_data/AR-GT-BUNDLES-02_RANGEL --exclude ".DS_Store"
  ```
  - All data: [BEWARE, SHOULD TAKE VERY LONG!]
  ```
  aws s3 sync raw_fmri_data s3://described-vs-experienced/raw_fmri_data --exclude ".DS_Store"
  ```
  - Template BIDS folder
  ```
  aws s3 sync bids_nifti_wface s3://described-vs-experienced/bids_nifti_wface --exclude ".DS_Store"
  ```

- Check if transfer is successful. Trailing "/" matters for the content
```
aws s3 ls s3://described-vs-experienced/bids_nifti_wface/
```

- Create E2 instance to test conversion on single subject. Instance needs:
  - access to S3 bucket (through policy)
  - heudiconv container (specified in AMI)
  - bids-validator container (specified in AMI)
  - DescribedVsLearned_fmri repo for the heuristics.py script

--> Create template instance using Amazon Linux 2 AMI
--> Install software (heudiconv, bidsvalidator, defacing stuff, mriqc, fmriprep)
--> Save current state of instance as AMI
--> Keep this AMI as fmri-preproc

- Run heudiconv on all subjects either on single EC2 or on cluster

- Defacing testing.

- Defacing on all

- Mriqc testing.

- Mriqc on all

- Fmriprep testing.

- Fmriprep on all
