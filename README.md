# SLI_fMRI
singularity shell --home Projects/SLI_fMRI/:/home/mydata /volatile/hackathon_tfmri_2018/hackathon-tfmri-2018.ubuntu.simg
python scripts/tfmri_spm_preproc.py -subject sub-S01 -block 1
