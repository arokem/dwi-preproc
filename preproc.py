"""
Preprocess raw DWI data.

Needs to be able to do the following:

1. Motion correction
2. Eddy current correction
3.


Dependencies
------------
For now, nothing.


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

""" 

import nibabel as nib

class DWI(object):
    def __init__(data, gtab)
        self.data = data
        self.gtab = gtab

classe DT6(object):
    def __init__(params)

        
