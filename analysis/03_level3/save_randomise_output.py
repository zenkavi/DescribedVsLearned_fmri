import shutil

# This is pretty inefficient. If you figure out a better way to iterate through 'nipype.interfaces.fsl.model.RandomiseOutputSpec' it would be better

def save_randomise_output(randomise_results, reg_path, mname, reg, tfce, sign):
    # save_randomise_output(randomise_results, reg_path, mname, suffix, tfce, sign)

    if len(randomise_results.outputs.tstat_files)>0:
        randomise_results.outputs.tstat_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.tstat_files):
            if tfce:
                shutil.move(cur_file, "%s/rand_tfce_tstat%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg) )
            else:
                shutil.move(cur_file, "%s/rand_cluster_tstat%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg) )
            print("***********************************************")
            print("Saved tstat_file for: %s %s"%(mname, reg))
            print("***********************************************")

    if len(randomise_results.outputs.fstat_files)>0:
        randomise_results.outputs.fstat_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.fstat_files):
            if tfce:
                shutil.move(cur_file,"%s/rand_tfce_fstat%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg) )
            else:
                shutil.move(cur_file,"%s/rand_cluster_fstat%s_%s_%s_%s.nii.gzz"%(reg_path, str(i+1), sign, mname, reg) )
            print("***********************************************")
            print("Saved fstat_file for: %s %s"%(mname, reg))
            print("***********************************************")

    if len(randomise_results.outputs.t_p_files)>0:
        randomise_results.outputs.t_p_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.t_p_files):
            if tfce:
                shutil.move(cur_file, "%s/rand_tfce_t_p%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg))
            else:
                shutil.move(cur_file, "%s/rand_cluster_t_p%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg))
            print("***********************************************")
            print("Saved t_p_file for: %s %s"%(mname, reg))
            print("***********************************************")

    if len(randomise_results.outputs.f_p_files)>0:
        randomise_results.outputs.f_p_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.f_p_files):
            if tfce:
                shutil.move(cur_file,"%s/rand_tfce_f_p%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg))
            else:
                shutil.move(cur_file,"%s/rand_tfce_f_p%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg))
            print("***********************************************")
            print("Saved f_p_file for: %s %s"%(mname, reg))
            print("***********************************************")

    if len(randomise_results.outputs.t_corrected_p_files)>0:
        randomise_results.outputs.t_corrected_p_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.t_corrected_p_files):
            if tfce:
                shutil.move(cur_file,"%s/rand_tfce_corrp_tstat%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg))
            else:
                shutil.move(cur_file,"%s/rand_cluster_corrp_tstat%s_%s_%s_%s.nii.gzz"%(reg_path, str(i+1), sign, mname, reg))
            print("***********************************************")
            print("Saved t_corrected_p_file for: %s %s"%(mname, reg))
            print("***********************************************")

    if len(randomise_results.outputs.f_corrected_p_files)>0:
        randomise_results.outputs.f_corrected_p_files.sort()
        for i, cur_file in enumerate(randomise_results.outputs.f_corrected_p_files):
            if tfce:
                shutil.move(cur_file,"%s/rand_tfce_corrp_fstat%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg))
            else:
                shutil.move(cur_file,"%s/rand_cluster_corrp_fstat%s_%s_%s_%s.nii.gz"%(reg_path, str(i+1), sign, mname, reg))
            print("***********************************************")
            print("Saved f_corrected_p_file for: %s %s"%(mname, reg))
            print("***********************************************")
