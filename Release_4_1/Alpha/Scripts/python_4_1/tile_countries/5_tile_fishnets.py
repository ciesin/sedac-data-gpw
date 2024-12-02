import arcpy, os
root = r'D:\gpw\release_4_1\input_data\tiled_countries\additional_countries'
dataFolder = r'D:\gpw\release_4_1\process_tiles'

isos = ['aus','bra','chn','ind','kaz']

for iso in isos:
    print iso
    arcpy.env.workspace = os.path.join(root,iso)
    arcpy.env.overwriteOutput = True
    
    gdbList = arcpy.ListWorkspaces()
    gdbList.sort()

    fishnet = os.path.join(dataFolder,iso+'.gdb',iso+'_fishnet')
    arcpy.MakeFeatureLayer_management(fishnet,'fish')

    for gdb in gdbList:
        arcpy.env.workspace = gdb
        tile = os.path.basename(gdb)[4:-4]
        print tile
        fc = arcpy.ListFeatureClasses("*"+tile)[0]

        dissolve = 'in_memory' + os.sep + iso + tile
        arcpy.Dissolve_management(fc,dissolve)
        
        outFishnet = os.path.join(gdb,iso+'_'+tile+'_fishnet')

        arcpy.SelectLayerByLocation_management('fish','intersect',dissolve)
        arcpy.CopyFeatures_management('fish',outFishnet)


print "done"

