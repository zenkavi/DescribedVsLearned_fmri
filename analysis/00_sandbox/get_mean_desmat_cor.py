#! /opt/miniconda-4.10.3/bin/python

from argparse import ArgumentParser
import glob
import os
import pandas as pd

parser = ArgumentParser()
parser.add_argument("--mnum", help="model number")
parser.add_argument("--reg_rt", help="regress rt")
parser.add_argument("--l1_path")
parser.add_argument("--l2_path")

args = parser.parse_args()
mnum = args.mnum
reg_rt = args.reg_rt
l1_path = args.l1_path
l2_path = args.l2_path

def get_mean_desmat_cor(mnum, reg_rt, l1_path):

    des_mats = glob.glob(os.path.join(l1_path, 'model%s_reg-rt%s/**/*design_matrix*'%(mnum, reg_rt)))

    beh_regs = pd.read_csv(des_mats[0]).columns
    to_filter = ['trans', 'rot', 'drift', 'framewise', 'scrub', 'constant', 'dvars']
    beh_regs = [x for x in beh_regs if all(y not in x for y in to_filter)]

    cor_mats = []
    for i, cur_des_mat in enumerate(des_mats):
        cur_des_mat = pd.read_csv(cur_des_mat)
        cor_mats.append(cur_des_mat[beh_regs].corr())

    df_concat = pd.concat(cor_mats)
    by_row_index = df_concat.groupby(df_concat.index)
    df_means = by_row_index.mean()

    return df_means

mean_cor_df = get_mean_desmat_cor(mnum, reg_rt, l1_path)

out_path = os.path.join(l2_path, 'model%s_reg-rt%s'%(mnum, reg_rt))

if not os.path.exists(out_path):
    os.makedirs(out_path)

mean_cor_df.to_csv(os.path.join(out_path, 'model%s_reg-rt%s_mean_desmat_cor.csv'%(mnum, reg_rt)))
