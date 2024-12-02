import arcpy, os
from arcpy import env

inFC = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\working\usa_ak.gdb\usa_ak_admin5'
outFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process\tiles\usaak'
kyttFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process\usa_ak.gdb'

tiles = {}
tileList = []
with arcpy.da.SearchCursor(inFC,["UBID","tile"]) as cursor:
    for row in cursor:
        tiles[row[0]] = row[1]
        if not row[1] in tileList:
            tileList.append(row[1])

env.workspace = kyttFolder

tableList = arcpy.ListTables()
tableList.sort()

for table in tableList[2:]:
    print table
    arcpy.AddField_management(table,"tile","TEXT","","",50)
    with arcpy.da.UpdateCursor(table,["USCID","tile"],"USCID IS NOT NULL") as cursor:
        for row in cursor:
            if row[0] in tiles:
                row[1] = tiles[row[0]]
            cursor.updateRow(row)

    print "added tile fields"

    for tile in tileList:
        tileGDB = os.path.join(outFolder,"usaak_"+tile+".gdb")
        if not arcpy.Exists(tileGDB):
            arcpy.CreateFileGDB_management(outFolder,"usaak_"+tile+".gdb")

        arcpy.TableToTable_conversion(table,tileGDB,"usaak_"+tile+table[5:],"tile = '"+tile+"'")




