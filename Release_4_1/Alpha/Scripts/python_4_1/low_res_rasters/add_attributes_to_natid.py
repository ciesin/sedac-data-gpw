#Jane Mills
#GPW
#Aggregate the national identifier grid

import arcpy, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

inFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\national_identifier_edits'
inFC = os.path.join(inFolder,'national_identifier_polygons.gdb','gpw_v4_national_identifier_grid_30_sec')
#inR = os.path.join(inFolder,'gpw_v4_national_identifier_30_sec.tif')
#r = os.path.join(inFolder,'gpw_v4_national_identifier_30_sec_con.tif')


fNames = []
fields = []
fList = arcpy.ListFields(inFC)
skip = ["OBJECTID","SHAPE","SHAPE_AREA","SHAPE_LENGTH"]
#skip = ["OID","VALUE","COUNT"]

for f in fList:
    if f.name.upper() in skip:
        pass
    else:
        fNames.append(f.name)
        fields.append(f)

gridDict = {}
with arcpy.da.SearchCursor(inFC,["GRIDCODE"]+fNames) as cursor:
    for row in cursor:
        gridDict[row[0]] = row[1:]

env.workspace = inFolder
rList = arcpy.ListRasters()
for r in rList:
    print r
    for f in fields:
        if f.type == 'Integer':
            arcpy.AddField_management(r,f.name,"LONG")
        elif f.type == 'String':
            arcpy.AddField_management(r,f.name,"TEXT","","",f.length)
        elif f.type == 'SmallInteger':
            arcpy.AddField_management(r,f.name,"SHORT")
        elif f.type == 'Double':
            arcpy.AddField_management(r,f.name,"DOUBLE")
        else:
            print "this field type doesn't belong"

    with arcpy.da.UpdateCursor(r,["Value"]+fNames) as cursor:
        for row in cursor:
            if row[0] in gridDict:
                row[1:] = gridDict[row[0]]
                cursor.updateRow(row)
            else:
                print "found an error"


