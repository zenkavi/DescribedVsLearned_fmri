#!/usr/bin/python3

import fmri_physio_log as fpl
import numpy as np
import os
from pathlib import Path

DATA_PATH='/shared/raw_fmri_data'
files_path = os.path.join(DATA_PATH, 'AR-GT-BUNDLES-02_RANGEL/Physio')
file_names = os.listdir(files_path)

content = Path(os.path.join(files_path, file_names[i])).read_text()

lines = content.splitlines()

line = lines.pop(0)

values = [int(v) for v in line.split(" ")[20:-1]]

ts = np.array([v for v in values if v < 5000])

*.resp line.split(" ")[20:-1]
*.puls line.split(" ")[20:-1]
*.ext line.split(" ")[25:-1]
*.ecg line.split(" ")[28:]
