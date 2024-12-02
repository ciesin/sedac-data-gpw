# check proportions
import arcpy
import os

arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'

gdbs = arcpy.ListWorkspaces("*","FILEGDB")

for gdb in gdbs:
    arcpy.env.workspace = gdb
    censusTable = arcpy.ListTables("*census*")[0]
##    print censusTable
    countCensus = arcpy.GetCount_management(
        arcpy.MakeTableView_management(censusTable,
                                       os.path.basename(gdb)[:-4]+"LY",'"' + "ATOTPOPBT" + '"' + " >= 0"))
##    print countCensus
    propTable = arcpy.ListTables("*proportion*")[0]
##    print propTable
    countProp = arcpy.GetCount_management(propTable)
##    print countProp
    if int(countCensus[0]) - int(countProp[0]) <> 0:
        print gdb
        print countCensus                 
        print countProp
