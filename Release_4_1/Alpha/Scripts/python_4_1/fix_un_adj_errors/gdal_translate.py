import os, arcpy

root = r'D:\gpw\release_4_1\global_tifs'
outFolder = r'D:\gpw\release_4_1\global_gdal_tifs'

arcpy.env.workspace = root
rList = [os.path.join(root,r) for r in arcpy.ListRasters()]
rList.sort()

for r in rList:
    rName = os.path.basename(r)
    print rName
    outR = os.path.join(outFolder,rName)
    os.system("gdal_translate -ot Float32 -co COMPRESS=LZW -of GTiff " + r + " " +  outR)

