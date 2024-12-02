#Jane Mills
#3/9/17
#summarize rasters and compare to tables

import arcpy, os
from arcpy import env

tableRoot = r'F:\gpw\release_4_1\process'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\validation\tiled_zonal_stats.gdb'

##env.workspace = outGDB
##
##tableList = arcpy.ListTables()
##tableList.sort()
##
##for table in tableList:
##    print table
##    with arcpy.da.SearchCursor(table,['SUM','MIN','MAX','STD']) as cursor:
##        for row in cursor:
##            print row[0]
##            print row[1]
##            print row[2]
##            print row[3]

env.workspace = tableRoot

gdbList = arcpy.ListWorkspaces()

for gdb in gdbList:
    tile = os.path.basename(gdb)[:-4]

    env.workspace = gdb

    table = arcpy.ListTables("*estimates")[0]

    fieldList = [f.name for f in arcpy.ListFields(table,"*E_A*")]
    fieldList.sort()

    for field in fieldList:
        if field[-3:] == "DSM" or field[-2:] == "DS":
            pass
        else:
            tCount = 0
            with arcpy.da.SearchCursor(table,field,field+' > 0') as cursor:
                for row in cursor:
                    tCount += row[0]

            print tile
            print field
            print tCount


