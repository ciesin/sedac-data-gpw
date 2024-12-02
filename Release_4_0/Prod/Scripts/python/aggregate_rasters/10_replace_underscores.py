#Jane Mills
#7/20/16
#GPW
#Rename the files to include the resolution

import arcpy, os
from arcpy import env

inRoot = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters_other_resolution'

resolutions = ['2_5_minute','0_25_degree','0_5_degree','1_degree']

for i in range(4):
    res = resolutions[i]
    print res
    
    asciiFolder = os.path.join(inRoot,res,'ascii')
    tifFolder = os.path.join(inRoot,res,'global_tifs')

    afList = os.listdir(asciiFolder)
    for af in afList:
        asciis = os.listdir(os.path.join(asciiFolder,af))
        for ascii in asciis:
            if ascii[-4:] == ".txt":
                print ascii
                inA = os.path.join(asciiFolder,af,ascii)
                outA = os.path.join(asciiFolder,af,ascii.replace("_","-"))
                os.rename(inA,outA)
            else:
                inA = os.path.join(asciiFolder,af,ascii)
                os.remove(inA)
    
    tfList = os.listdir(tifFolder)
    for tf in tfList:
        env.workspace = os.path.join(tifFolder,tf)
        rList = arcpy.ListRasters()
        for r in rList:
            print r
            inR = os.path.join(tifFolder,tf,r)
            outR = os.path.join(tifFolder,tf,r.replace("_","-"))
            arcpy.Rename_management(inR,outR)

    print "complete"
