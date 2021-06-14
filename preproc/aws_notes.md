
- Transfer data to S3

  - One subject
  ```
  aws s3 sync AR-GT-BUNDLES-02_RANGEL s3://described-vs-experienced/raw_fmri_data/AR-GT-BUNDLES-02_RANGEL --exclude ".DS_Store"
  ```

  - All data: [BEWARE, SHOULD TAKE VERY LONG!]
  ```
  aws s3 sync ~/Downloads/GTavares_2017_arbitration/raw_fmri_data s3://described-vs-experienced/raw_fmri_data/ --exclude ".DS_Store"
  ```

  - Template BIDS folder
  ```
  aws s3 sync ~/Downloads/GTavares_2017_arbitration/bids_nifti_wface s3://described-vs-experienced/bids_nifti_wface/ --exclude ".DS_Store"
  ```


- Create E2 instance to test conversion on single subject. Instance needs:
  - access to S3 bucket (through policy)
  - heudiconv container (specified in AMI)
  - bids-validator container (specified in AMI)
  - DescribedVsLearned_fmri repo for the heuristics.py script

```
```

- Run heudiconv on all subjects either on single EC2 or on cluster

- Defacing testing. Instance needs:
  - access to S3 bucket (through policy)
  - any software for defacing
  - DescribedVsLearned_fmri repo for my own defacing script

- Defacing on all

- Mriqc testing. Instance needs:
  - access to S3 bucket (through policy)
  - mriqc container
  - DescribedVsLearned_fmri repo for my own defacing script

- Mriqc on all

- Fmriprep testing. Instance needs:
  - access to S3 bucket (through policy)
  - fmriprep container
  - DescribedVsLearned_fmri repo for my own defacing script

- Fmriprep on all
