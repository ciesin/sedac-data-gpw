# migrate input population tables
# this script cleans up the gdbs which were manually copied from
# \\Dataserver0\gpw\GPW4\Release_4_0\Beta\Gridding\country\pop_tables
# to
# \\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables

# 2-5-2016
# Kytt MacManus

# import libraries
import arcpy, os

# define input and output directories
inWS = r'F:\usa\names'

# list workspaces
arcpy.env.workspace = inWS
workspaces = arcpy.ListWorkspaces("*")
for workspace in workspaces:
    # describe the workspace
    workDesc = arcpy.Describe(workspace)
    # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
    if str(workDesc.workspaceType)=="FileSystem":
        workspace = workspace + os.sep + os.path.basename(workspace)+".gdb" 
    # clean the estimates tables out of the workspace
    arcpy.env.workspace = workspace
    tbls = arcpy.ListTables("*estimates*")
    for tbl in tbls:
        arcpy.Delete_management(tbl)
        print "Deleted " + tbl
    # clean the proportions tables out of the workspace
    tbls = arcpy.ListTables("*proportion*")
    for tbl in tbls:
        arcpy.Delete_management(tbl)
        print "Deleted " + tbl


            
