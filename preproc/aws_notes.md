
- Transfer data to S3

```
aws s3 sync ~/Downloads/GTavares_2017_arbitration/raw_fmri_data s3://described-vs-experienced/raw_fmri_data/ --exclude ".DS_Store"
aws s3 sync ~/Downloads/GTavares_2017_arbitration/bids_nifti_wface s3://described-vs-experienced/bids_nifti_wface/ --exclude ".DS_Store"
```

- Create E2 instance to test conversion on single subject. Instance needs:

  - access to S3 bucket
  - heudiconv
  - bids-validator
  - DescribedVsLearned_fmri repo

```
```

- Run heudiconv on all subjects either on single EC2 or on cluster

- Defacing testing

- Defacing on all

- Mriqc testing

- Mriqc on all

- Fmriprep testing

- Fmriprep on all
