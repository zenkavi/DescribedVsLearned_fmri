import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes

def infotodict(seqinfo):

    # paths done in BIDS format
    t1w = create_key('sub-{subject}/anat/sub-{subject}_T1w') #anat
    t2w = create_key('sub-{subject}/anat/sub-{subject}_T2w') #anat
    task = create_key('sub-{subject}/func/sub-{subject}_task-bundles_run-{item:01d}_bold') #func
    sbref = create_key('sub-{subject}/func/sub-{subject}_task-bundles_run-{item:01d}_sbref') #func
    fmap_pos = create_key('sub-{subject}/fmap/sub-{subject}_pos') #fmap
    fmap_neg = create_key('sub-{subject}/fmap/sub-{subject}_neg') #fmap

    info = {t1w: [], t2w: [], task: [], sbref: [], fmap_pos: [], fmap_neg: []}

    #each row of dicominfo.tsv
    for idx, s in enumerate(seqinfo):

        if (s.TE == 2.56) and ('T1w' in s.protocol_name) and ('NORM' in s.image_type):
            info[t1w].append(s.series_id)

        if (s.TE == 206) and ('T2w' in s.protocol_name) and ('NORM' in s.image_type):
            info[t2w].append(s.series_id)

        if ('BOLD_MB' in s.protocol_name):
            if (s.dim4 == 892):
                info[task].append({'item': s.series_id})
            elif (s.dim4 == 1):
                info[sbref].append({'item': s.series_id})

        if (s.TE == 50):
            if ('Fieldmap_Pos' in s.protocol_name):
                info[fmap_pos].append({'item': s.series_id})
            elif ('Fieldmap_Neg' in s.protocol_name):
                info[fmap_neg].append({'item': s.series_id})

    return info
