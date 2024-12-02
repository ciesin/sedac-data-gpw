import arcpy, os
from arcpy import env

inFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\working'
outFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process\tiles'
kyttFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process'

arcpy.env.workspace = inFolder

gdbs = arcpy.ListWorkspaces("*working*","FILEGDB")
gdbs.sort()

for gdb in gdbs[1:]:
    iso = os.path.basename(gdb)[:3]
    print iso

    env.workspace = gdb

    tileFC = arcpy.ListFeatureClasses("*boundaries_2010")[0]

    tiles = {}
    tileList = []
    with arcpy.da.SearchCursor(tileFC,["UBID","tile"]) as cursor:
        for row in cursor:
            tiles[row[0]] = row[1]
            if not row[1] in tileList:
                tileList.append(row[1])

    outGDB = os.path.join(kyttFolder,iso+".gdb")
    env.workspace = outGDB

    fcName = arcpy.ListFeatureClasses("*boundaries_2010*")[0]
    fc = os.path.join(outGDB,fcName)
    arcpy.AddField_management(fc,"tile","TEXT","","",50)
    with arcpy.da.UpdateCursor(fc,["UBID","tile"]) as cursor:
        for row in cursor:
            if row[0] in tiles:
                row[1] = tiles[row[0]]
            else:
                print row[0] + " not in tile FC"
            cursor.updateRow(row)

    table = arcpy.ListTables()[0]
    arcpy.AddField_management(table,"tile","TEXT","","",50)
    with arcpy.da.UpdateCursor(table,["UBID","tile"],"UBID IS NOT NULL") as cursor:
        for row in cursor:
            if row[0] in tiles:
                row[1] = tiles[row[0]]
            cursor.updateRow(row)

    print "added tile fields"
    
    tablePath = os.path.join(outGDB,table)
    for tile in tileList:
        print tile
        tileGDB = os.path.join(outFolder,iso,iso+"_"+tile+".gdb")
        arcpy.CreateFileGDB_management(os.path.join(outFolder,iso),iso+"_"+tile+".gdb")

        arcpy.FeatureClassToFeatureClass_conversion(fc,tileGDB,iso+"_"+tile+fcName[3:],"tile = '"+tile+"'")
        arcpy.TableToTable_conversion(tablePath,tileGDB,iso+"_"+tile+table[3:],"tile = '"+tile+"'")




