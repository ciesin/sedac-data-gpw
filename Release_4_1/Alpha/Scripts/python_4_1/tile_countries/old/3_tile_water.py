import arcpy, os

clipFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\fishnets\country_boundaries_admin0\tiles'
outFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process\tiles'
waterFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process'

isos = os.listdir(clipFolder)
isos.sort()

for iso in isos:
    if iso == "usa":
        print "skipping usa"
    else:
        print iso
        arcpy.env.workspace = os.path.join(clipFolder,iso)

        fcList = arcpy.ListFeatureClasses()
        fcList.sort()

        water = os.path.join(waterFolder,iso+".gdb",iso+"_water_features")

        for fc in fcList:
            tile = fc[4:-4]
            print tile
            outFC = os.path.join(outFolder,iso,iso+"_"+tile+".gdb",iso+"_"+tile+"_water_features")
            arcpy.Clip_analysis(water,os.path.join(clipFolder,iso,fc),outFC)
        print "clipped"

print "done"

