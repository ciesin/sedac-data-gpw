import os
import arcpy

# The number of jobs is equal to the number of files
workspace = r'\\Dataserver0\gpw\GPW4\InputData\fishnets\bra_states'
outWS = r'\\Dataserver0\gpw\GPW4\InputData\fishnets'
arcpy.env.workspace = workspace
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()
# iterate
for gdb in gdbs:
    ISO = os.path.basename(gdb)[:3]
    # Create Output Folder
    outputRoot = outWS
    gdbName = os.path.basename(gdb)[:-4]
    outGDB = outputRoot + os.path.sep + outGDB + ".gdb"
    if not arcpy.Exists(outGDB):
##        arcpy.CreateFileGDB_management(outputRoot,gdbName)
        print "Created " + outGDB
        arcpy.AddMessage("Created " + outGDB)
    else:
        print outGDB + " already exists"
        arcpy.AddMessage(outGDB + " already exists")
