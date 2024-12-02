#Jane Mills
#7/27/16
#GPW
#Rename the folders to include the resolution

import arcpy, os
from arcpy import env

inRoot = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters_other_resolution'

resolutions = ['2_5_minute','0_25_degree','0_5_degree','1_degree']
tifnames = ['-2-5-min','-qtr-deg','-half-deg','-one-deg']
asciinames = ['-2-5-min-ascii','-qtr-deg-ascii','-half-deg-ascii','-one-deg-ascii']

for i in range(4):
    res = resolutions[i]
    tname = tifnames[i]
    aname = asciinames[i]
    print res
    
    asciiFolder = os.path.join(inRoot,res,'ascii')
    tifFolder = os.path.join(inRoot,res,'global_tifs')

    afList = os.listdir(asciiFolder)
    for af in afList:
        inFA = os.path.join(asciiFolder,af)
        outFA = os.path.join(asciiFolder,af+aname)
        os.rename(inFA,outFA)
    
    tfList = os.listdir(tifFolder)
    for tf in tfList:
        inFT = os.path.join(tifFolder,tf)
        outFT = os.path.join(tifFolder,tf+tname)
        os.rename(inFT,outFT)

    print "complete"
