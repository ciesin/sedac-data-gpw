#Jane Mills
#11/27/2017
#rename asciis

import os, csv

root = r'F:\gpw\gpw4_rev10_fixed_extents\centroids'
print "processing"

fileList = os.listdir(root)
fileList.sort()

for f in fileList:
    extLoc = f.find(".")
    ext = f[extLoc:]
    name = f[:extLoc]
    iso = name[:-10].lower()
    print iso
    newName = "gpw_v4_admin_unit_center_points_population_estimates_rev10_"+iso+ext
    new = os.path.join(root,newName)
    os.rename(os.path.join(root,f),new)

