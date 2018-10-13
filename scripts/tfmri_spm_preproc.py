
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
import argparse

parser = argparse.ArgumentParser(description='Preprocess data in BIDS structure')
parser.add_argument('-subject', type=str, help='subject name in BIDS format')
parser.add_argument('-block', type=int, help='block (=session in BIDS) number')
args = parser.parse_args()


# Global parameters
BIDS_DATA_DIR = "/home/mydata/"
N_JOBS = 1

import os, glob

# subject = "sub-S01"
# block = 3
filename_prefix = args.subject + '_Block_%i' % args.block
funcfile = glob.glob(os.path.join(BIDS_DATA_DIR, "sourcedata", args.subject, 'ses-V%i' % args.block , "func", "sub-*bold.nii.gz"))[0]
anatfile = glob.glob(os.path.join(BIDS_DATA_DIR, "sourcedata", args.subject, 'ses-V%i' % args.block, "anat", "sub-*T1w.nii.gz"))[0]
outdir = '/home/mydata/results'

# Define SPM backend
from pypreprocess.configure_spm import _SPM_DEFAULTS
os.environ["SPM_MCR"] = "/i2bm/local/bin/spm12"
_SPM_DEFAULTS["spm_dir_template"].insert(0, "/i2bm/local/spm{VERSION_NB}-standalone")

# Imports

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
    print('Starting pre-processing...')
    subject_data = do_subject_preproc(
        subject_data,
        deleteorient=False,
        slice_timing=False,
        ref_slice=0,
        TR=2.5,
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

subject_data = do_preproc(funcfile, anatfile, args.subject, decimate=False)
subject_data.func


# #### Perform some quality checks for one subject
# 
# First we can check the motion parameters:
plot_spm_motion_parameters(
    subject_data.nipype_results["realign"].outputs.realignment_parameters,
    title="Realign: estimated motion.")
plt.savefig(os.path.join(outdir, filename_prefix + '_motion_params.png'))
plt.close()


# We can also check the coregistration:
plot_registration(
    anatfile,
    subject_data.nipype_results["coreg"].outputs.coregistered_files,
    close=False,
    cut_coords=(-10, 20, 5),
    title="Coregister outline.")
plt.savefig(os.path.join(outdir, filename_prefix + '_coregistration.png'))
plt.close()


# And the normalization:
from pypreprocess.nipype_preproc_spm_utils import SPM_T1_TEMPLATE
plot_registration(
    SPM_T1_TEMPLATE,
    subject_data.nipype_results["normalize"].outputs.normalized_source,
    close=False,
    cut_coords=(-10, 0, 5),
    title="Normalization outline.")
plt.savefig(os.path.join(outdir, filename_prefix + '_normalization.png'))
plt.close()


# Finally we can check the time serie:
diff_results = multi_session_time_slice_diffs([funcfile])
axes = plot_tsdiffs(diff_results, use_same_figure=True)
diff_results = multi_session_time_slice_diffs(subject_data.func)
axes = plot_tsdiffs(diff_results, use_same_figure=True)
plt.savefig(os.path.join(outdir, filename_prefix + '_time_series.png'))
plt.close()