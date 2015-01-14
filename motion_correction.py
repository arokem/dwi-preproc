
# coding: utf-8

# In[40]:

import nibabel as nb
import nipy
import numpy as np
import matplotlib.pyplot as plt
import nipy.algorithms.registration
import ip_utils


# In[41]:

# Library of Files
path = '../../../../scratch/cpoetter/8472/'
folder = ['6/8472_6_1','12/8472_12_1','8/8472_8_1','10/8472_10_1', '6_ec/8472_6_1', '12_ec/8472_12_1']
sigma_folder = ['6/S6_caipi_pe0_maps', '12/S12_caipi_pe0_maps', '8/S8_mica_pe0_maps', '10/S10_mica_pe0_maps', '6_ec/S6_caipi_pe0_maps', '12_ec/S12_caipi_pe0_maps']


# In[42]:

# Files to be motion corrected
t1_files = [path+folder[0]+'.nii.gz',
            path+folder[1]+'.nii.gz']

# Registration is for T1 images not DWI iamges -> base registration on first b0 image
images = [nb.squeeze_image(nb.load(f)) for f in t1_files]
data = [f.get_data()[:,:,:,0] for f in images]


# In[43]:

# Base registration on an average images, because after resampling data is smoothed, so every dataset needs to be resampled
average = np.zeros(data[0].shape)
for i, vox in np.ndenumerate(average):
    temp_sum = 0
    for f in data:
        temp_sum += f[i]
    average[i] = temp_sum / len(data) 
average_image = nb.Nifti1Image(average, images[0].get_affine())


# In[44]:

# Register every image (and direction) to the average one and save it
for i in xrange(len(images)):
    nifti = nb.four_to_three(images[i])
    reg = nipy.algorithms.registration.HistogramRegistration(nifti[0], average_image, similarity='crl1', interp='tri')
    T = reg.optimize('rigid')
    
    rotated = []
    for j in xrange(len(nifti)):
        corrected = nipy.algorithms.registration.resample(nifti[j], T.inv(), reference=average_image)
        to_nifti = nb.Nifti1Image(corrected.get_data(), corrected.affine)
        rotated.append(to_nifti)
        
    result = nb.concat_images(rotated)    
    registered_file = path + folder[i] + 'motion_corrected.nii.gz'
    nb.save(result, registered_file)

