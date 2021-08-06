import shutil

# This is pretty inefficient. If you figure out a better way to iterate through 'nipype.interfaces.fsl.model.RandomiseOutputSpec' it would be better

def save_randomise_output(randomise_results, reg_path, mnum, reg, tfce):

    if len(randomise_results.outputs.tstat_files)>0:
        randomise_results.outputs.tstat_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.tstat_files):
            if tfce:
                shutil.move(cur_file, "%s/rand_%s_%s_tstat%s_tfce.nii.gz"%(reg_path,mnum, reg, str(i+1)) )
            else:
                shutil.move(cur_file, "%s/rand_%s_%s_tstat%s_cluster.nii.gz"%(reg_path,mnum, reg, str(i+1)) )
            print("***********************************************")
            print("Saved tstat_file for: %s %s"%(mnum, reg))
            print("***********************************************")

    if len(randomise_results.outputs.fstat_files)>0:
        randomise_results.outputs.fstat_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.fstat_files):
            if tfce:
                shutil.move(cur_file,"%s/rand_%s_%s_fstat%s_tfce.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            else:
                shutil.move(cur_file,"%s/rand_%s_%s_fstat%s_cluster.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            print("***********************************************")
            print("Saved fstat_file for: %s %s"%(mnum, reg))
            print("***********************************************")

    if len(randomise_results.outputs.t_p_files)>0:
        randomise_results.outputs.t_p_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.t_p_files):
            if tfce:
                shutil.move(cur_file, "%s/rand_%s_%s_t_p%s_tfce.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            else:
                shutil.move(cur_file, "%s/rand_%s_%s_t_p%s_cluster.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            print("***********************************************")
            print("Saved t_p_file for: %s %s"%(mnum, reg))
            print("***********************************************")

    if len(randomise_results.outputs.f_p_files)>0:
        randomise_results.outputs.f_p_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.f_p_files):
            if tfce:
                shutil.move(cur_file,"%s/rand_%s_%s_f_p%s_tfce.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            else:
                shutil.move(cur_file,"%s/rand_%s_%s_f_p%s_cluster.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            print("***********************************************")
            print("Saved f_p_file for: %s %s"%(mnum, reg))
            print("***********************************************")

    if len(randomise_results.outputs.t_corrected_p_files)>0:
        randomise_results.outputs.t_corrected_p_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.t_corrected_p_files):
            if tfce:
                shutil.move(cur_file,"%s/rand_%s_%s_tfce_corrp_tstat%s.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            else:
                shutil.move(cur_file,"%s/rand_%s_%s_cluster_corrp_tstat%s.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            print("***********************************************")
            print("Saved t_corrected_p_file for: %s %s"%(mnum, reg))
            print("***********************************************")

    if len(randomise_results.outputs.f_corrected_p_files)>0:
        randomise_results.outputs.f_corrected_p_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.f_corrected_p_files):
            if tfce:
                shutil.move(cur_file,"%s/rand_%s_%s_tfce_corrp_fstat%s.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            else:
                shutil.move(cur_file,"%s/rand_%s_%s_cluster_corrp_fstat%s.nii.gz"%(reg_path,mnum, reg, str(i+1)))
            print("***********************************************")
            print("Saved f_corrected_p_file for: %s %s"%(mnum, reg))
            print("***********************************************")
