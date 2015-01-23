# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import nibabel as nib
import nipy
import numpy as np
import matplotlib.pyplot as plt
import nipy.algorithms.registration
import ip_utils
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import nibabel.freesurfer.io as freesurfer

# <codecell>

def T1_alignment(t1_image, dwi_image, gtab, label_image):
    
    # Filter White Matter and Corpus Callosum
    label_data = label_image.get_data()
    freesurfer_label_list = [[2,41,77,85,1004,2004], # Label 1 -> White Matter
                             [251,252,253,254,255]]  # Label 2 -> Corpus Callosum
    number_categories = len(freesurfer_label_list)
    
    rearanged_label_list = np.zeros(label_data.shape + (number_categories,)).astype(bool)
    for category in range(number_categories):
        for label in freesurfer_label_list[category]:
            rearanged_label_list[..., category] = np.logical_or(rearanged_label_list[..., category], (label_data == label))
        
    new_label_image = nib.Nifti1Image(rearanged_label_list.astype(float), label_image.affine, header=label_image.header)     
    new_label_images = nib.four_to_three(new_label_image)

    # Register T1 Image to DWI b0 Image
    t1_image_squeezed = nib.squeeze_image(t1_image)
    
    dwi_data = dwi_image.get_data()
    dwi_data_b0s = dwi_data[..., gtab.b0s_mask]
    dwi_data_b0 = np.mean(dwi_data_b0s, axis=3)
    dwi_image_b0 = nib.Nifti1Image(dwi_data_b0, dwi_image.get_affine(), header=dwi_image.header)

    reg = nipy.algorithms.registration.HistogramRegistration(dwi_image_b0, t1_image_squeezed, similarity='crl1', interp='tri')
    T = reg.optimize('rigid')

    # Resample Labels according to DWI Images
    # Each on it's own to prevent mistakes in transformation/rounding
    labels_interpolated = np.zeros(dwi_image_b0.shape)
    for category in range(number_categories):
        image_temp = nipy.algorithms.registration.resample(new_label_images[category], T, reference=dwi_image_b0, interp_order=1)
        label_temp = np.round(image_temp.get_data()).astype(int)
        labels_interpolated += label_temp * (category+1)
    
    return labels_interpolated

# <codecell>

# Load Files
path = '../../../../scratch/cpoetter/8631/'
t1_path = '../../../../scratch/anatomy/chris/mri/T1.mgz'
label_path = '../../../../scratch/anatomy/chris/mri/aparc+aseg.mgz'
dwi_path = path + '5/dwi_ec.nii.gz'
bval = path + 'bval'
bvec = path + 'bvec'

t1_image = nib.load(t1_path)
dwi_image = nib.load(dwi_path)
label_image = nib.load(label_path)
bvals, bvecs = read_bvals_bvecs(bval, bvec)
gtab = gradient_table(bvals, bvecs)

# Run Mask Alignment
mask = T1_alignment(t1_image, dwi_image, gtab, label_image)

# Save mask
to_nifti = nib.Nifti1Image(mask, dwi_image.affine)
white_matter_file = path + 'labels.nii.gz'
nib.save(to_nifti, white_matter_file)

