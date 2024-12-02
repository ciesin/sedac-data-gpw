# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 12:12:52 2018

@author: jmills
"""

import arcpy, os, shutil

#outFolder = r'D:\gpw\release_4_11\national_identifier'
#outFolder = r'D:\gpw\release_4_11\watermask'
inFolder = r'D:\gpw\release_4_1\country_tifs'
outFolder = r'D:\gpw\release_4_11\maua'

#outAreaFolder = os.path.join(outFolder,'areakm')
outAreaFolder = os.path.join(outFolder,'maskedareakm')

isoList = os.listdir(inFolder)
multiIsos = []

for iso in isoList:
    isoFolder = os.path.join(inFolder,iso)
    #fileList = [f for f in os.listdir(isoFolder) if "_AREAKM" in f]
    fileList = [f for f in os.listdir(isoFolder) if "_MASKEDAREAKM" in f]
    
    if len(fileList) == 0:
        multiIsos.append(iso)
        print("not copying: "+iso)

    for f in fileList:    
        shutil.copy(os.path.join(isoFolder,f),os.path.join(outAreaFolder,f))

#multiIsos.pop(multiIsos.index("cas"))
#multiIsos.pop(multiIsos.index("bla"))

for iso in multiIsos:
    print(iso)
    isoFolder = os.path.join(inFolder,iso)
    subdirs = os.listdir(isoFolder)
    mergeList = []
    
    for subdir in subdirs:
        subFolder = os.path.join(isoFolder,subdir)
        #fileList = [f for f in os.listdir(subFolder) if f[-11:] == "_AREAKM.tif"]
        fileList = [f for f in os.listdir(subFolder) if f[-17:] == "_MASKEDAREAKM.tif"]
        mergeList.append(os.path.join(subFolder,fileList[0]))
        
    #arcpy.MosaicToNewRaster_management(mergeList,outAreaFolder, iso+"_AREAKM.tif", "", "32_BIT_FLOAT", "", "1", "SUM","FIRST")
    arcpy.MosaicToNewRaster_management(mergeList,outAreaFolder, iso+"_MASKEDAREAKM.tif", "", "32_BIT_FLOAT", "", "1", "SUM","FIRST")

mergeList = []
for iso in isoList:
    isoFolder = os.path.join(inFolder,iso)
    fileList = [f for f in os.listdir(isoFolder) if f[-25:] == "_MEAN_MASKEDADMINAREA.tif"]
    
    if len(fileList) == 0:
        isoFolder = os.path.join(inFolder,iso)
        subdirs = os.listdir(isoFolder)
        for subdir in subdirs:
            subFolder = os.path.join(isoFolder,subdir)
            fileList = [f for f in os.listdir(subFolder) if f[-25:] == "_MEAN_MASKEDADMINAREA.tif"]
            mergeList.append(os.path.join(subFolder,fileList[0]))

    else:
        mergeList.append(os.path.join(isoFolder,fileList[0]))

arcpy.MosaicToNewRaster_management(mergeList,outFolder, "MEAN_MASKEDADMINAREA.tif", "", "32_BIT_FLOAT", "", "1", "MEAN","FIRST")
