
######################################
# S3: Data storage
######################################
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

######################################
# EC2: Computing
######################################
- EC2 and cluster specifications

--> Create template instance using Amazon Linux 2 AMI
--> Install software (heudiconv, bidsvalidator, defacing stuff, mriqc, fmriprep, study script repo - DescribedVsLearned_fmri)
--> Give access to S3 bucket
--> Save current state of instance as AMI
--> Keep this AMI as fmri-preproc
--> Data management:
  - Root is EBS.
  - Testing writes to this. When instance is destroyed testing output is destroyed too.
  - When running for all subjects read from and write to S3; with potential intermediate steps like Lustre SCRATCH

- Test the following on single instance and run for all subjects on cluster
  - Heudiconv
  - Defacing
  - Mriqc
  - Fmriprep
