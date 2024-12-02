import arcpy, os
rootFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\tiled_countries'
outRoot = r'D:\gpw\release_4_1\input_data\tiled_countries\additional_countries'

isos = ['aus','bra','chn','ind','kaz']

for iso in isos:
    print iso
    inGDB = os.path.join(rootFolder,iso+'.gdb')
    arcpy.env.workspace = inGDB
    fcList = arcpy.ListFeatureClasses()
    fcList.sort()
    
    waterList = filter(lambda x: 'water' in x, fcList)
    waterList.sort()
    adminList = filter(lambda x: 'water' not in x, fcList)
    adminList.sort()

    for i in range(len(waterList)):
        water = waterList[i]
        admin = adminList[i]
        tile = admin[4:]
        print tile
        
        outGDB = os.path.join(outRoot,iso,iso+"_"+tile+'.gdb')
        arcpy.CreateFileGDB_management(os.path.join(outRoot,iso),iso+"_"+tile+'.gdb')

        arcpy.CopyFeatures_management(water,os.path.join(outGDB,water))
        arcpy.CopyFeatures_management(admin,os.path.join(outGDB,admin))

print "done"

