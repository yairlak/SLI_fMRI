import os, glob
import argparse

parser = argparse.ArgumentParser(description='Arrange files in BIDS standard')
parser.add_argument('-src', type=str, help='Path to source folder with all nifti files')
parser.add_argument('-dest', type=str, help='Path to destination folder, e.g., /SLI_fMRI/')
parser.add_argument('--num-subject', type=int, help='Subject number')
args = parser.parse_args()

# Generate folders for current subject in BIDS structure
os.makedirs(os.path.join(args.dest, 'sourcedata'), exist_ok=True)
try:
    os.makedirs(os.path.join(args.dest, 'sourcedata','sub-S%02i' % args.num_subject), exist_ok=False)
except:
    print('Error: Subject folder already exists. Remove it or change subject number.')
    exit()
os.makedirs(os.path.join(args.dest, 'sourcedata','sub-S%02i' % args.num_subject, 'ses-V1'), exist_ok=False)

# EDIT this according to the desired subfolder names and their corresponding identifiers in the file names:
file_types_identifiers = ['_MPRAGE_', '_cmrr_', '_diff_', '_localizer_', '_tirm_']
subfolder_names = ['anat', 'func', 'dwi', 'localizer', 'tirm']

# Generate the desired folders and move the files to their from the source folder
for identifier, subfolder_name in zip(file_types_identifiers, subfolder_names):
    print(subfolder_name, identifier)
    folder_name = os.path.join(args.dest, 'sourcedata','sub-S%02i' % args.num_subject, 'ses-V1', subfolder_name)
    os.makedirs(folder_name, exist_ok=True)
    print(os.path.join(args.src, '*'+identifier+'*'))
    file_names = glob.glob(os.path.join(args.src, '*'+identifier+'*'))
    for f in file_names:
        print(f)
        prefix = 'sub-S%02i_' % args.num_subject
        bodyname = os.path.splitext(os.path.basename(f))[0]
        bodyname = os.path.splitext(bodyname)[0]
        if identifier == '_MPRAGE_':
            suffix = '_T1w.nii.gz'
        elif identifier == '_cmrr_':
            suffix = '_bold.nii.gz'
        else:
            suffix = '.nii.gz'
        new_name = os.path.join(folder_name, prefix + bodyname + suffix) 
        os.rename(f, new_name)
        print('nifti file moved to: ' + new_name)