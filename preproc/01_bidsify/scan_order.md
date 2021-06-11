# Expected scan order

- Localizer

5 blocks of:
- Sbref
- Task
- Fieldmap pos
- Fieldmap neg

2 blocks of:
- T1-anat

2 blocks of:
- T2-anat

- T2-clinical

# Subjects with different files/orders:

- 02: anatomicals in separate sub-directory
- 06: Has mid-scan localizer (block 14)
- 08: Subdirectory of dicoms has different name structure
- 10: Has mid-scan localizer and anatomicals (blocks 14-19)
- 17: Has mid-scan localizer (block 14)
- **EXCLUDE** 21: No subject 21
- **EXCLUDE** 26: Only three task runs and no anatomicals 
- 27: No T2-clinical
