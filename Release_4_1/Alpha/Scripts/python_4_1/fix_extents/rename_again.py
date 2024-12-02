#Jane Mills
#11/27/2017
#rename asciis

import os, csv

root1 = r'F:\gpw\gpw4_rev10_fixed_extents\ascii'
root2 = r'F:\gpw\gpw4_rev10_fixed_extents\gdal_tifs'
print "processing"

for root in [root1] + [root2]:
    fileList = os.listdir(root)
    fileList.sort()

    for f in fileList:
        if "cntm" in f and "population" in f:
            print f
            newName = f.replace("_cntm_","_")
            os.rename(os.path.join(root,f),os.path.join(root,newName))
        if "dens" in f and "population" in f:
            print f
            newName = f.replace("_dens_","_")
            os.rename(os.path.join(root,f),os.path.join(root,newName))
            
