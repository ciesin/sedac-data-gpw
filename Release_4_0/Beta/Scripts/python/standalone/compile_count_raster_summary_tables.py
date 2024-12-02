## compile estimates_summary table

import arcpy,os,sys, datetime
startTime = datetime.datetime.now()
# define roots
outRoot = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\validate\diagnostics.gdb'
schemaIn =r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb\count_raster_summary'
outTable = outRoot + os.sep + 'count_raster_summary_09232015'
# create summary table to append to
if arcpy.Exists(outTable):
    arcpy.Delete_management(outTable)
arcpy.CopyRows_management(schemaIn,outTable)
    
# define workspaces
globalSpace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\rasters'
usaSpace = globalSpace + os.sep + "usa"
braSpace = globalSpace + os.sep + "bra"
canSpace = globalSpace + os.sep + "can"
grlSpace = globalSpace + os.sep + "grl"
rusSpace = globalSpace + os.sep + "rus"
workspaces = [globalSpace,usaSpace,braSpace,canSpace,grlSpace,rusSpace]
gdb_list = []
# iterate workspaces and assemble paths
for ws in workspaces:
    arcpy.env.workspace = ws
    gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
    gdbs.sort()
    gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
    for gdbt in gdb_temp:
        gdb_list.append(gdbt)    
gdb_list.sort()
# define empty list to add estimateTable views to
estimatesTables = []
# iterate gdb paths
for inputGDB in gdb_list:
    arcpy.env.workspace = inputGDB
    iso = os.path.basename(inputGDB)[:-4].upper()
    if len(arcpy.ListTables('*summary'))==1:
        inputTable = arcpy.ListTables('*summary')[0]
    else:
        arcpy.AddMessage('Either the summary table is missing or there are multiple versions. Correct and rerun')
        print 'Either the summary  table is missing or there are multiple versions. Correct and rerun'
        sys.exit()
    estimatesTableView = arcpy.MakeTableView_management(inputTable,iso)
    estimatesTables.append(estimatesTableView)
print "Created merge list, it has " + str(len(estimatesTables)) + " tables."
for table in estimatesTables:
    arcpy.Append_management(table,outTable,"NO_TEST")
    print "Appended " + str(table)
print "Script Complete"
print datetime.datetime.now()-startTime
