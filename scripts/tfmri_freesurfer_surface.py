
# coding: utf-8

# ## Toward the surface using FreeSurfer
# 
# If you are working with large cohort this part may not be relevant for your study. Otherwise it may help to refine the analysis results.
# 
# #### Compute the cortex surface from the T1w image using FreeSurfer
# 

# In[ ]:

# Imports
import os
import glob
from joblib import Parallel, delayed
import nipype.interfaces.freesurfer as freesurfer
import nipype.interfaces.fsl as fsl

# Global parameters
BIDS_DATA_DIR = "/home/mydata/localizer"
N_JOBS = 20
PROCESS = True

# List all T1 files available
t1_files = glob.glob(os.path.join(BIDS_DATA_DIR, "sourcedata", "sub-*", "ses-*",
                                  "anat", "sub-*T1w.nii.gz"))

# Create a small function to perform the requested task
# For tutorial purposed the command is just printed, set
# the global parameter 'PROCESS' to True to execute the command:
# around 8 hours processing!
# Note that images are first reoriented.
def nipype_reconall(t1path, t2path=None):
    splitpath = t1path.split(os.sep)
    
    # Reorientation using FSL
    reodir = os.path.join(
        BIDS_DATA_DIR, "derivatives", "reorient_{0}".format(splitpath[-3]),
        splitpath[-4])
    if not os.path.isdir(reodir):
        os.makedirs(reodir)
    reopath = []
    for path in (t1path, t2path):
        if path is not None:
            reopath.append(os.path.join(reodir, os.path.basename(path)))
        else:
            reopath.append(None)
            continue
        reorient = fsl.Reorient2Std(
            in_file=path,
            out_file=reopath[-1])
        if PROCESS:
            reorient.run()
    t1path, t2path = reopath
    
    # Segmentation using FreeSurfer
    fsdir = os.path.join(
        BIDS_DATA_DIR, "derivatives", "freesurfer_{0}".format(splitpath[-3]))
    if not os.path.isdir(fsdir):
        os.makedirs(fsdir)
    reconall = freesurfer.ReconAll(
        subject_id=splitpath[-4],
        directive="all",
        subjects_dir=fsdir,
        T1_files=t1path)
    if t2path is not None:
        reconall.inputs.T2_file = t2path
        reconall.inputs.use_T2 = True
    if PROCESS:
        reconall.run()

    return reconall.cmdline

# Call the previous function over all the available t1 files
print(freesurfer.Info.version())
print("fsl-" + fsl.Info.version())
print("-" * 20)
Parallel(n_jobs=N_JOBS, verbose=20)(delayed(nipype_reconall)(path) for path in t1_files)


# ###### Note
# 
# Do not run this command, it takes several hours. All the results have been precomputed for you.
# Depending of the input image resolution you may add the 'highres' and 'expert' command line arguments (https://surfer.nmr.mgh.harvard.edu/fswiki/SubmillimeterRecon).
# 
# #### Perform some quality checks
# 
# First check the FreeSurfer returncode:

# In[4]:

# Imports
import os
import glob

# Global parameters
BIDS_DATA_DIR = "/home/mydata/localizer"

fslogs = glob.glob(os.path.join(BIDS_DATA_DIR, "derivatives", "freesurfer_*", "*",
                                "scripts", "recon-all-status.log"))
for path in fslogs:
    for line in open(path):
        if line.strip():
            last_non_empty_line = line
    if "finished without error" in last_non_empty_line:
        status = "OK"
    else:
        status = "ERROR"
    print(path, status)


# Then, check the Euler number as suggested in AFG Rosen et al. Quantitative assessment of structural image quality, NeuroImage 2018. Using the default threshold value, all euler numbers must be greater than -217:

# In[8]:

# Imports
import os
import glob
import subprocess
from pprint import pprint

data = {}
for hemi in ("lh", "rh"):
    surfs = glob.glob(os.path.join(BIDS_DATA_DIR, "derivatives", "freesurfer_*", "*",
                                   "surf", "{0}.orig.nofix".format(hemi)))
    for path in surfs:
        cmd = ["mris_euler_number", path]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        exitcode = process.returncode
        if exitcode != 0:
            raise  ValueError("Oups!")
        euler_number = int(stderr.split("\n")[0].rsplit("=", 1)[1].split("-->")[0])
        sid = path.split(os.sep)[-3]
        if sid not in data:
            data[sid] = 0
        data[sid] += euler_number * 0.5
pprint(data)


##### Project the functional volume on the cortex using FreeSurfer

# In[4]:

# Imports
import os
import glob
from joblib import Parallel, delayed
import nipype.interfaces.freesurfer as freesurfer
import nipype.interfaces.fsl as fsl

# Global parameters
BIDS_DATA_DIR = "/home/mydata/localizer"
N_JOBS = 20
PROCESS = False

# List all T1 files available
t1_files = glob.glob(os.path.join(BIDS_DATA_DIR, "sourcedata", "sub-*", "ses-*",
                                  "anat", "sub-*T1w.nii.gz"))

# Coregister the func dataset to the FreeSurfer anatomical using BBR
# For tutorial purposed the command is just printed, uncomment
# the last line to execute the command.
def nipype_bbregister(t1path):
    splitpath = t1path.split(os.sep)
    sub_fsdir = os.path.join(BIDS_DATA_DIR, "derivatives", "freesurfer_{0}".format(splitpath[-3]),
                             splitpath[-4])
    if not os.path.isdir(sub_fsdir):
        os.mkdir(sub_fsdir)
    outdir = os.path.join(BIDS_DATA_DIR, "derivatives", "freesurfer_projection_{0}".format(splitpath[-3]),
                          splitpath[-4])
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    funcpath = os.path.join(BIDS_DATA_DIR, "derivatives", "spmpreproc_{0}".format(splitpath[-3]),
                            splitpath[-4], "wrr{0}_{1}_task-localizer_bold.nii.gz".format(
                                splitpath[-4], splitpath[-3]))
    assert os.path.isfile(funcpath), funcpath
    basename = os.path.basename(funcpath).replace(".nii.gz", "")
    os.environ["SUBJECTS_DIR"] = os.path.dirname(sub_fsdir)
    bbreg = freesurfer.BBRegister(
        subject_id=splitpath[-4],
        source_file=funcpath,
        init="fsl",
        contrast_type="t2",
        dof=6,
        fsldof=6,
        reg_frame=0,
        out_fsl_file=os.path.join(outdir, basename + ".fsl.mat"),
        out_reg_file=os.path.join(outdir, basename + ".reg.dat"))
    print(bbreg.cmdline)
    if PROCESS:
        bbreg.run()

# Call the previous function over all the available t1 files
print(freesurfer.Info.version())
print("-" * 20)
#Parallel(n_jobs=N_JOBS)(delayed(nipype_bbregister)(path) for path in t1_files)
for path in t1_files:
    nipype_bbregister(path)

# Project the coregistered functional dataset to the FreeSurfer cortex
# For tutorial purposed the command is just printed, uncomment
# the last line to execute the command.
def nipype_mri_vol2surf(t1path, hemi):
    splitpath = t1path.split(os.sep)
    fsdir = os.path.join(BIDS_DATA_DIR, "derivatives", "freesurfer_{0}".format(splitpath[-3]))
    outdir = os.path.join(BIDS_DATA_DIR, "derivatives", "freesurfer_projection_{0}".format(splitpath[-3]),
                          splitpath[-4])
    funcpath = os.path.join(BIDS_DATA_DIR, "derivatives", "spmpreproc_{0}".format(splitpath[-3]),
                            splitpath[-4], "wrr{0}_{1}_task-localizer_bold.nii.gz".format(
                                splitpath[-4], splitpath[-3]))
    assert os.path.isfile(funcpath), funcpath
    basename = os.path.basename(funcpath).replace(".nii.gz", "")
    regfile = os.path.join(outdir, basename + ".reg.dat")
    assert os.path.isfile(regfile), regfile
    #if not os.path.isfile(regfile):
    #    open(regfile, "wt").close()
    vol2surf = freesurfer.SampleToSurface(
        hemi=hemi,
        source_file=funcpath,
        reg_file=regfile,
        sampling_method="average",
        sampling_units="frac",
        sampling_range=(0.2, 0.8, 0.1),
        out_type="gii",
        out_file=os.path.join(outdir, basename + ".{0}.gii".format(hemi)),
        subjects_dir=fsdir)
    print(vol2surf.cmdline)
    if PROCESS:
        vol2surf.run()
    
# Call the previous function over all the available t1 files
print("\n\n")
print(freesurfer.Info.version())
print("-" * 20)
#Parallel(n_jobs=N_JOBS)(delayed(nipype_mri_vol2surf)(path) for path in t1_files)
for path in t1_files:
    for hemi in ("lh", "rh"):
        nipype_mri_vol2surf(path, hemi)
    


##### Vetex to vertex correspondance using FreeSurfer

# In[10]:

# Imports
import os
import glob
from joblib import Parallel, delayed
import nipype.interfaces.freesurfer as freesurfer
import nipype.interfaces.fsl as fsl

# Global parameters
BIDS_DATA_DIR = "/home/mydata/localizer"
N_JOBS = 20
PROCESS = True

# Project the texture to the fsaverage using FreeSurfer and smooth the data
# For tutorial purposed the command is just printed, uncomment
# the last line to execute the command.
def nipype_mri_surf2surf(t1path, hemi):
    splitpath = t1path.split(os.sep)
    fsdir = os.path.join(BIDS_DATA_DIR, "derivatives", "freesurfer_{0}".format(splitpath[-3]))
    outdir = os.path.join(BIDS_DATA_DIR, "derivatives", "freesurfer_projection_{0}".format(splitpath[-3]),
                          splitpath[-4])
    funcpath = os.path.join(BIDS_DATA_DIR, "derivatives", "spmpreproc_{0}".format(splitpath[-3]),
                            splitpath[-4], "wrr{0}_{1}_task-localizer_bold.nii.gz".format(
                                splitpath[-4], splitpath[-3]))
    assert os.path.isfile(funcpath), funcpath
    basename = os.path.basename(funcpath).replace(".nii.gz", "")
    texturefile = os.path.join(outdir, basename + ".{0}.gii".format(hemi))
    smoothfile = os.path.join(outdir, basename + ".s5.{0}.gii".format(hemi))
    if not os.path.isfile(texturefile):
        raise ValueError("Oups!: {0}".format(path))
    if not os.path.isfile(smoothfile):
        open(smoothfile, "wt").close()
    surf2surf = freesurfer.SurfaceSmooth(
        in_file=texturefile,
        hemi=hemi,
        subject_id=splitpath[-4],
        fwhm=5,
        out_file=smoothfile,
        subjects_dir=fsdir)
    print(surf2surf.cmdline)
    if PROCESS:
        surf2surf.run()
    surf2surf = freesurfer.SurfaceTransform(
        hemi=hemi,
        source_subject=splitpath[-4],
        source_file=smoothfile,
        target_subject="ico",
        target_ico_order=7,
        out_file=os.path.join(outdir, basename + ".ico7.s5.{0}.gii".format(hemi)),
        subjects_dir=fsdir)
    print(surf2surf.cmdline)
    if PROCESS:
        surf2surf.run()
    
# Call the previous function over all the available t1 files
print("\n\n")
print(freesurfer.Info.version())
print("-" * 20)
#Parallel(n_jobs=N_JOBS)(delayed(nipype_mri_surf2surf)(path) for path in t1_files)
for path in t1_files:
    for hemi in ("lh", "rh"):
        nipype_mri_surf2surf(path, hemi)
    

