## compile estimates_summary table

import arcpy,os,sys

estimatesTables = []
outRoot = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\diagnostics.gdb'
prepTable =r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb\estimates_summary_prep'
outTable = outRoot + os.sep + 'estimates_summary_usa'
statsTable = outTable + "_dissolve"
arcpy.CopyRows_management(prepTable,outTable)

workspace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
usaSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'
workspaces = [usaSpace]
gdb_list = []
for ws in workspaces:
    arcpy.env.workspace = ws
    gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
    gdbs.sort()
##    gdb_list.append(gdbs[0])
    gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
    for gdbt in gdb_temp:
        gdb_list.append(gdbt)    

for inputGDB in gdb_list:
    arcpy.env.workspace = inputGDB
    iso = os.path.basename(inputGDB)[:-4]
    if len(arcpy.ListTables('*_estimates_summary'))==1:
        inputTable = arcpy.ListTables('*_estimates_summary')[0]
    else:
        arcpy.AddMessage('Either the estimates_summary table is missing or there are multiple versions. Correct and rerun')
        print 'Either the estimates_summary  table is missing or there are multiple versions. Correct and rerun'
        sys.exit()
    estimatesTableView = arcpy.MakeTableView_management(inputTable,iso)
    estimatesTables.append(estimatesTableView)
print "Created merge list, it has " + str(len(estimatesTables)) + " tables."
for table in estimatesTables:
    arcpy.Append_management(table,outTable,"NO_TEST")
    print "Appended " + str(table)
arcpy.AddField_management(outTable,"ISO","TEXT","","",10)
arcpy.CalculateField_management(outTable,"ISO",'str(!FIRST_ISO!)[:3]',"PYTHON")
