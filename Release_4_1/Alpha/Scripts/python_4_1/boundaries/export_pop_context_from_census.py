#Jane Mills
#1/19/2017
#Export pop context rows
import os, arcpy

censusGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\highlevel_census.gdb'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\pop_context.gdb'

arcpy.env.workspace = censusGDB
arcpy.env.overwriteOutput = True

tableList = arcpy.ListTables()
tableList.sort()

for table in tableList:
    iso = table[:3]
    print iso

    fieldList = arcpy.ListFields(table,"POP_CONTEXT")
    if len(fieldList) == 1:
        print "found pop context"
        arcpy.MakeTableView_management(table,"layer")

        arcpy.SelectLayerByAttribute_management("layer","NEW_SELECTION","POP_CONTEXT IS NOT NULL")

        result = arcpy.GetCount_management("layer")
        count = int(result.getOutput(0))

        if count > 0:
            arcpy.CopyRows_management("layer",os.path.join(outGDB,table))
            print "copied rows"
