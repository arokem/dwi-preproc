"""
Preprocess raw DWI data.

Needs to be able to do the following:

1. Motion correction
2. Eddy current correction
3.


Dependencies
------------
nipy

Steps taken by dtiInit:

1. load diffusion data
2. initialize a struct array with folder information
3. Find a T1w file 
4. Reorient the data to standard, unflipped, axial order
5. Get a phase encode direction
6. Get the gradient table
7. Check for missing data, exclude indicated volumes
8. Rotate the bvecs to the canonical orientations (based on step 4)
9. Compute mean b0 (assumes no motion between b0 measurements!)
10. Motion correction and Eddy current correction.
11. Compute the alignment from DWI to T1w
12. Resample the DWIs (considering both alignment and motion correction)
13. Reorient the bvecs
14. DTI
15. Build the dt6.files
16. Create t1pdd.png (as QC)
17. Log things like the version of the code that was run (SVN revision)

For eddy current correction, look at mrAnatXformCoords (lines 99-119). The main
thing there is computing a second order 3D polynomial, which is applied to the
coordinates, in addition to the rigid body transform.

""" 


import argparse as arg

import numpy as np

import nibabel as nib
import dipy.core.gradients as grad
import nipy.algorithms.registration as reg


class DWI(object):
    def __init__(fname, fbval, fbvec):
        self.fname = fname
        self.fbval = fbval
        self.fbvec = fbvec

    gtab = property(get_gtab)
    def get_gtab(self):
        self.gtab = grad.gradient_table(self.fbval, self.fbvec)
        
    data = property(get_data)
    def get_data(self):
        """
        """
        self._data = nib.load(self.fname).get_data()
        
    b0_sig = property(get_b0_sig)
    def get_S0(self):
        self._b0_sig = self.data[..., self.gtab.b0s_mask]

    dw_sig = property(get_dw_sig)
    def get_dw_sig(self)
        self._dw_sig = self.data[..., ~self.gtab.b0s_mask]
    
    def register_b0(self):
        images = [nib.squeeze_image(nib.Nifti1Image(d.T, data_aff)) for d in
                  self.b0_sig.T]
        ref = images[0]
        aligned_b0_ni = motion_correction(images, ref)
        mean_b0_aligned = np.mean(aligned_b0_ni)
        
    def
        

def motion_correction(images, ref, similarity='crl1', interp='tri',
                      jitter_init=False):
    """

    """
    aligned = []
    for im in images:
        reggy = reg.HistogramRegistration(im, 
                                          ref, 
                                          similarity=similarity,
                                          interp=interp)

        #
        if jitter_init:
            # Give it a non-zero starting point:
            T = reg.Rigid()
            my44 = np.eye(4)
            jitter = np.random.randn(3)
            my44[:3, 3] = 
            T.from_matrix44(my44)

        # Optimize from there:
        T = reggy.optimize(T)
        # Resample without interpolation:
        corrected = reg.resample(im, T.inv(), reference=ref)
        aligned.append(nib.Nifti1Image(corrected.get_data(), corrected.affine))

    return nib.concat_images(aligned)

parser = arg.ArgumentParser('Preprocess DWI data')

if __name__=="__main__":
    data = nib.load(fdata)
    gtab = grad.gradient_table(fbval, fbvec)
    
