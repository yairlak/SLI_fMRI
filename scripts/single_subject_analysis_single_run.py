
##### Analysis of a single session, single subject fMRI dataset


###############################################################################
import os
import matplotlib.pyplot as plt
from os.path import join
from nilearn.image import concat_imgs, mean_img
anat_img = '/home/yl254115/Projects/SLI_fMRI/sourcedata/sub-S01/ses-V1/anat/sub-S01_ZA_260718_MPRAGE_iso1mm_T1w.nii.gz'
# fmri_img = '/home/yl254115/Projects/SLI_fMRI/derivatives/spmpreproc_ses-V2/sub-S01/wrrsub-S01_ZA_260718_cmrr_mbep2d_157vola_bold.nii.gz'
fmri_img = '/home/yl254115/Projects/SLI_fMRI/derivatives/spmpreproc_ses-V1/sub-S01/wrrsub-S01_ZA_260718_cmrr_mbep2d_157vol_bold.nii.gz'
mean_img = mean_img(fmri_img)
events_file = '/home/yl254115/Projects/SLI_fMRI/sourcedata/sub-S01/logs/log_subject_5_run_2.txt'
outdir = '/home/yl254115/Projects/SLI_fMRI/results'
subject = 'sub-S01'
block = 1
broca = (-38, 16, 50)
A1 = (-40, -28, 6)
V1 = (-28, -96, -6)
roi_name = 'A1'
roi = eval(roi_name)
cond1 = 'ZM'
cond2 = 'SILENCE'
contrast_name = subject + '_block_%i_' % block + cond1 +'_minus_' + cond2 + '_roi_' + roi_name
from numpy import array
contrast_vecs = {'FIL':     array([1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]),
                 'SVOZ':    array([0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]),
                 'SZVO':    array([0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]),
                 'ZM':      array([0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.]),
                 'SILENCE': array([0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]),
                 'SVO':     array([0., 0., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]),
                 'NULL':    array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]),
                 'ALL':     array([1., 0., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.])}
conditions = {cond1: contrast_vecs[cond1], cond2:contrast_vecs[cond2]}
curr_contrast = conditions[cond1] - conditions[cond2]

smoothing = 8

###############################################################################
# We can display the first functional image and the subject's anatomy:
from nilearn.plotting import plot_stat_map, plot_anat, plot_img, show
# plot_img(fmri_img)
plot_anat(anat_img)
plt.savefig(join(outdir, subject + '_anatomy.png'))
plt.close()

###############################################################################
# Specifying the experimental paradigm (events file)
# ----------------------------------------------------
import pandas as pd
# with open(events_file, 'r') as f:
#     events = f.readlines()
# events = [l.split('\t') for l in events]
events = pd.read_table(events_file)
fn = lambda row: row.FixEnd - row.AudioStart# define a function for the new column
col = events.apply(fn, axis=1) # get column data with an index
events = events.assign(duration=col.values)
events = events.rename(index=str, columns = {"AudioStart":"onset", "Cond":"trial_type"})
events = events.filter(['onset','duration','trial_type'], axis=1)
events.onset = events.onset.astype(float)
events.duration = events.duration.astype(float)
events.trial_type = events.trial_type.astype(str)
events.loc[events.trial_type == 'nan', 'trial_type'] = 'SILENCE'
print(events)

# Tweak the events file
events['duration'].values[:] = 2.5
# for index, row in events.iterrows():
#     if row['trial_type'] != 'nan':
#         events['onset'].values[int(index)] = row['onset'] + 2.5
print(events)

###############################################################################
# Performing the GLM analysis
# ---------------------------
###############################################################################
# Parameters of the first-level model
#
# * t_r=2.5(s) is the time of repetition of acquisitions
# * noise_model='ar1' specifies the noise covariance model: a lag-1 dependence
# * standardize=False means that we do not want to rescale the time
# series to mean 0, variance 1
# * hrf_model='spm' means that we rely on the SPM "canonical hrf"
# * model (without time or dispersion derivatives)
# * drift_model='cosine' means that we model the signal drifts as slow oscillating time functions
# * period_cut=160(s) defines the cutoff frequency (its inverse actually).
from nistats.first_level_model import FirstLevelModel
from nilearn.image import high_variance_confounds
from nistats.reporting import plot_design_matrix

confounds = pd.DataFrame(high_variance_confounds(fmri_img, percentile=1))
fmri_glm = FirstLevelModel(t_r=2.5,
                           noise_model='ar1',
                           standardize=False,
                           hrf_model='spm',
                           drift_model='cosine',
                           period_cut=160, smoothing_fwhm=smoothing)

fmri_glm = fmri_glm.fit(fmri_img, events, confounds=confounds)
design_matrix = fmri_glm.design_matrices_[0]
# Save the design matrix image to disk
if not os.path.exists(outdir): os.mkdir(outdir)
plot_design_matrix(design_matrix, output_file=join(outdir, subject + '_block_%i_' % block + '_design_matrix.png'))
plt.close()
print('Design matrix plot saved to: ' + join(outdir, subject + '_block_%i_' % block + '_design_matrix.png'))
# The first column contains the expected reponse profile of regions which are sensitive to the stimuli in the condition
if cond1 in design_matrix.columns:
    plt.plot(design_matrix[cond1])
    plt.xlabel('Time (sec)')
    plt.title('Expected ' + cond1 + ' Response')
    plt.savefig(join(outdir, cond1 + '_expected_response.png'))

###############################################################################
# Detecting voxels with significant effects
# -----------------------------------------
#
# To access the estimated coefficients (Betas of the GLM model), we
# created constrast with a single '1' in each of the columns: The role
# of the contrast is to select some columns of the model --and
# potentially weight them-- to study the associated statistics. So in
# a nutshell, a contrast is a weighted combination of the estimated
# effects.  Here we can define canonical contrasts that just consider
# the two condition in isolation ---let's call them "conditions"---
# then a contrast that makes the difference between these conditions.

from nistats.reporting import plot_contrast_matrix
plot_contrast_matrix(curr_contrast, design_matrix=design_matrix, output_file=join(outdir, contrast_name + '_contrast.png'))

###############################################################################
# Below, we compute the estimated effect. It is in BOLD signal unit,
# but has no statistical guarantees, because it does not take into
# account the associated variance.
eff_map = fmri_glm.compute_contrast(curr_contrast, output_type='effect_size')

###############################################################################
# In order to get statistical significance, we form a t-statistic, and
# directly convert is into z-scale. The z-scale means that the values
# are scaled to match a standard Gaussian distribution (mean=0,
# variance=1), across voxels, if there were now effects in the data.
z_map = fmri_glm.compute_contrast(curr_contrast, output_type='z_score')

###############################################################################
# Plot thresholded z scores map.
#
# We display it on top of the average
# functional image of the series (could be the anatomical image of the
# subject).  We use arbitrarily a threshold of 3.0 in z-scale. We'll
# see later how to use corrected thresholds.  we show to display 3
# axial views: display_mode='z', cut_coords=3

plot_stat_map(z_map, bg_img=mean_img, threshold=3,
              display_mode='ortho', cut_coords=roi, black_bg=True,
              title= contrast_name + ' (Z>3)', output_file=join(outdir, contrast_name + '_zmap.png'))

###############################################################################
# Statistical signifiance testing. One should worry about the
# statistical validity of the procedure: here we used an arbitrary
# threshold of 3.0 but the threshold should provide some guarantees on
# the risk of false detections (aka type-1 errors in statistics). One
# first suggestion is to control the false positive rate (fpr) at a
# certain level, e.g. 0.001: this means that there is.1% chance of
# declaring active an inactive voxel.

from nistats.thresholding import map_threshold
_, threshold = map_threshold(z_map, level=.001, height_control='fpr')
print('Uncorrected p<0.001 threshold: %.3f' % threshold)
plot_stat_map(z_map, bg_img=mean_img, threshold=threshold,
              display_mode='ortho', cut_coords=roi, black_bg=True,
              title=contrast_name + ' (p<0.001)', output_file=join(outdir, contrast_name + '_zmap_corrected.png'))

###############################################################################
# The problem is that with this you expect 0.001 * n_voxels to show up
# while they're not active --- tens to hundreds of voxels. A more
# conservative solution is to control the family wise errro rate,
# i.e. the probability of making ony one false detection, say at
# 5%. For that we use the so-called Bonferroni correction

_, threshold = map_threshold(z_map, level=.05, height_control='bonferroni')
print('Bonferroni-corrected, p<0.05 threshold: %.3f' % threshold)
plot_stat_map(z_map, bg_img=mean_img, threshold=threshold,
              display_mode='ortho', cut_coords=roi, black_bg=True,
              title=contrast_name + ' (p<0.05, corrected)', output_file=join(outdir, contrast_name + '_zmap_bonferroni.png'))

###############################################################################
# This is quite conservative indeed !  A popular alternative is to
# control the false discovery rate, i.e. the expected proportion of
# false discoveries among detections. This is called the false
# disovery rate

_, threshold = map_threshold(z_map, level=.05, height_control='fdr')
print('False Discovery rate = 0.05 threshold: %.3f' % threshold)
plot_stat_map(z_map, bg_img=mean_img, threshold=threshold,
              display_mode='ortho', cut_coords=roi, black_bg=True,
              title= contrast_name + ' (fdr=0.05)', output_file=join(outdir, contrast_name + '_zmap_fdr.png'))

###############################################################################
# Finally people like to discard isolated voxels (aka "small
# clusters") from these images. It is possible to generate a
# thresholded map with small clusters removed by providing a
# cluster_threshold argument. here clusters smaller than 10 voxels
# will be discarded.

clean_map, threshold = map_threshold(
    z_map, level=.05, height_control='fdr', cluster_threshold=10)
plot_stat_map(clean_map, bg_img=mean_img, threshold=threshold,
              display_mode='ortho', cut_coords=roi, black_bg=True,
              title= contrast_name + ' (fdr=0.05), clusters > 10 voxels', output_file=join(outdir, contrast_name + '_zmap_large_clusters.png'))

###############################################################################
# We can save the effect and zscore maps to the disk
z_map.to_filename(join(outdir, contrast_name + '_z_map.nii.gz'))
eff_map.to_filename(join(outdir, contrast_name + '_eff_map.nii.gz'))

###############################################################################
# Report the found positions in a table

from nistats.reporting import get_clusters_table
table = get_clusters_table(z_map, stat_threshold=threshold,
                           cluster_threshold=20)
print(table)

###############################################################################
# the table can be saved for future use

table.to_csv(join(outdir, contrast_name + '_table.csv'))

###############################################################################
# Performing an F-test
#
# "active vs rest" is a typical t test: condition versus
# baseline. Another popular type of test is an F test in which one
# seeks whether a certain combination of conditions (possibly two-,
# three- or higher-dimensional) explains a significant proportion of
# the signal.  Here one might for instance test which voxels are well
# explained by combination of the active and rest condition.
import numpy as np
effects_of_interest = np.vstack((conditions[cond1], conditions[cond2]))
plot_contrast_matrix(effects_of_interest, design_matrix, output_file=join(outdir, contrast_name + '_contrast_matrix.png'))

###############################################################################
# Specify the contrast and compute the correspoding map. Actually, the
# contrast specification is done exactly the same way as for t
# contrasts.

z_map = fmri_glm.compute_contrast(effects_of_interest,
                                  output_type='z_score')

###############################################################################
# Note that the statistic has been converted to a z-variable, which
# makes it easier to represent it.

clean_map, threshold = map_threshold(
    z_map, level=.05, height_control='fdr', cluster_threshold=10)
plot_stat_map(clean_map, bg_img=mean_img, threshold=threshold,
              display_mode='ortho', cut_coords=roi, black_bg=True,
              title='Effects of interest (fdr=0.05), clusters > 10 voxels', output_file=join(outdir, contrast_name + '_effects_of_interest_map.png'))