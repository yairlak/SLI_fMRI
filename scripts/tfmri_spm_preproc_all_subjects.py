
# coding: utf-8

# ## fMRI preprocessings using the pypreprocess Python package.
# 
# 
# * Slice timing (optional).
# * Realign (mandatory): motion correction - adjust for movement between slices.
# * Coregistration (mandatory): overlay structural and functional images - link
#    functional scans to anatomical scan.
# * Normalization (mandary): warp images to fit to a standard template brain.
# * Smoothing (optional): increase signal-to-noise ratio.
# * SNAPs (optional): compute some snaps assessing the different processing
#    steps.
# 
# #### All the imports & global parameters


# Global parameters
BIDS_DATA_DIR = "/home/mydata/"
N_JOBS = 1

funcfile = "/home/mydata/sourcedata/sub-S01/ses-V1/func/sub-S01_ZA_260718_cmrr_mbep2d_157vol_bold.nii.gz"
anatfile = "/home/mydata/sourcedata/sub-S01/ses-V1/anat/sub-S01_ZA_260718_MPRAGE_iso1mm_T1w.nii.gz"
outdir = "/home/mydata/results"
subject = "sub-S01"

# Define SPM backend
import os
from pypreprocess.configure_spm import _SPM_DEFAULTS
os.environ["SPM_MCR"] = "/i2bm/local/bin/spm12"
_SPM_DEFAULTS["spm_dir_template"].insert(0, "/i2bm/local/spm{VERSION_NB}-standalone")

# Imports
import glob
import shutil
import nibabel
from joblib import Parallel, delayed
from pypreprocess.subject_data import SubjectData
from pypreprocess.nipype_preproc_spm_utils import do_subject_preproc
from pypreprocess.reporting.check_preprocessing import plot_registration
from pypreprocess.reporting.check_preprocessing import plot_segmentation
from pypreprocess.reporting.check_preprocessing import plot_spm_motion_parameters
from pypreprocess.time_diff import plot_tsdiffs
from pypreprocess.time_diff import multi_session_time_slice_diffs
import pylab as plt


##### Define a function that grab the data for one subject and execute the preprocessing


def do_preproc(funcfile, anatfile, subject, decimate=False):
    """ Function that performs the preprocessing.
    
    Parameters
    ----------
    funcfile: str
        the functional volume.
    anatfile: str
        the anatomical volume.
    subject: str
        the subject identifier.
    decimate: bool, default False
        if set reduce the input functional volume size (loose information).
        
    Returns
    -------
    subject_data: object
        a structure that contains the output results.
    """   
    # Grab the data
    splitpath = anatfile.split(os.sep)
    outdir = os.path.join(
        BIDS_DATA_DIR, "derivatives", "spmpreproc_{0}".format(splitpath[-3]),
        subject)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    local_funcfile = os.path.join(outdir, os.path.basename(funcfile))
    if not os.path.isfile(local_funcfile):
        shutil.copy2(funcfile, local_funcfile)
    if decimate:
        im = nibabel.load(local_funcfile)
        dec_im = nibabel.Nifti1Image(im.get_data()[..., :3], im.affine)
        nibabel.save(dec_im, local_funcfile)
    local_anatfile = os.path.join(outdir, os.path.basename(anatfile))
    if not os.path.isfile(local_anatfile):
        shutil.copy2(anatfile, local_anatfile)
    #cwd = os.getcwd()
    os.chdir(outdir)
    subject_data = SubjectData(
        subject_id=subject,
        func=local_funcfile,
        anat=local_anatfile,
        output_dir=outdir,
        caching=True)
    
    # Start processing
    subject_data = do_subject_preproc(
        subject_data,
        deleteorient=False,
        slice_timing=False,
        ref_slice=0,
        TR=2,
        TA=None,
        realign=True,
        realign_reslice=True,
        register_to_mean=True,
        realign_software="spm",
        coregister=True,
        coregister_reslice=True,
        coreg_anat_to_func=False,
        coregister_software="spm",
        segment=False,
        normalize=True,
        fwhm=0,
        anat_fwhm=0,
        func_write_voxel_sizes=[3, 3, 3],
        anat_write_voxel_sizes=[1, 1, 1],
        hardlink_output=True,
        report=False,
        tsdiffana=True,
        parent_results_gallery=None,
        last_stage=True,
        preproc_undergone=None,
        prepreproc_undergone="",
        caching=True)
    
    return subject_data


##### Start preprocessing for one subject

subject_data = do_preproc(funcfile, anatfile, subject, decimate=False)
subject_data.func


# #### Perform some quality checks for one subject
# 
# First we can check the motion parameters:

plot_spm_motion_parameters(
    subject_data.nipype_results["realign"].outputs.realignment_parameters,
    title="Realign: estimated motion.")
plt.show()
plt.close()


# We can also check the coregistration:

plot_registration(
    anatfile,
    subject_data.nipype_results["coreg"].outputs.coregistered_files,
    close=False,
    cut_coords=(-10, 20, 5),
    title="Coregister outline.")
plt.show()
plt.close()


# And the normalization:

# In[8]:

from pypreprocess.nipype_preproc_spm_utils import SPM_T1_TEMPLATE
plot_registration(
    SPM_T1_TEMPLATE,
    subject_data.nipype_results["normalize"].outputs.normalized_source,
    close=False,
    cut_coords=(-10, 0, 5),
    title="Normalization outline.")
plt.show()
plt.close()


# Finally we can check the time serie:

# In[10]:

diff_results = multi_session_time_slice_diffs([funcfile])
axes = plot_tsdiffs(diff_results, use_same_figure=True)
diff_results = multi_session_time_slice_diffs(subject_data.func)
axes = plot_tsdiffs(diff_results, use_same_figure=True)
plt.show()
plt.close()


##### Start preprocessing for all subjects

# List all T1 & func files available
subjects = glob.glob1(os.path.join(BIDS_DATA_DIR, "sourcedata"), "sub-*")
t1_files = []
func_files = []
for sid in subjects:
    t1_files.extend(glob.glob(os.path.join(BIDS_DATA_DIR, "sourcedata", sid, "ses-*",
                                           "anat", "sub-*T1w.nii.gz")))
    func_files.extend(glob.glob(os.path.join(BIDS_DATA_DIR, "sourcedata", sid, "ses-*",
                                             "func", "sub-*bold.nii.gz")))
assert len(subjects) == len(t1_files)
assert len(subjects) == len(func_files)
                      
print("-" * 20)
Parallel(n_jobs=N_JOBS, verbose=20, backend="multiprocessing")(
    delayed(do_preproc)(funcfile, anatfile, subject)
                        for funcfile, anatfile, subject in zip(func_files, t1_files, subjects))



