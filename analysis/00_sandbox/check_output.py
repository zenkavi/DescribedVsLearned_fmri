#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
import glob
import os
import pandas as pd

parser = ArgumentParser()
parser.add_argument("--mnum")
parser.add_argument("--reg_rt")
parser.add_argument("--level")

args = parser.parse_args()
mnum = args.mnum
reg_rt = args.reg_rt
level = int(args.level)

if level == 1:
    ...

if level == 2:
    ...

if level == 3:
    ...
