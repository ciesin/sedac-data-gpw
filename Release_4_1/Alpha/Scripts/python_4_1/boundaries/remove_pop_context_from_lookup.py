#Jane Mills
#1/13/2017
#remove pop context rows from lookup tables

import os, arcpy

lookupGDB = r'F:\GPW\calculate_gubids\lookup_tables.gdb'

arcpy.env.workspace = lookupGDB
arcpy.env.overwriteOutput = True

tableList = arcpy.ListTables()
tableList.sort()

for table in tableList[10:]:
    iso = table[:3]
    print iso

    arcpy.MakeTableView_management(table,"layer")

    arcpy.SelectLayerByAttribute_management("layer","NEW_SELECTION","POP_CONTEXT IS NOT NULL")

    result = arcpy.GetCount_management("layer")
    count = int(result.getOutput(0))

    if count > 0:
        arcpy.DeleteRows_management("layer")
        print "deleted rows:", count

