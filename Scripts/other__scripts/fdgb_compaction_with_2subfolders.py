#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      edwhitfi
#
# Created:     27/07/2014
# Copyright:   (c) edwhitfi 2014
# Licence:     
#-------------------------------------------------------------------------------

import arcpy, os
import datetime

# set counter
startTime = datetime.datetime.now()

arcpy.env.workspace = arcpy.GetParameterAsText(0)
##arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
workspace = arcpy.env.workspace

arcpy.AddMessage(os.path.basename(workspace) + " folder")
print os.path.basename(workspace) + " folder"

# 1. List file GDBs
gdbs = arcpy.ListWorkspaces("*","FileGDB")
gdbs.sort()

for gdb in gdbs:

    try:
# Compact file gdb
        fileGDBname = os.path.basename(gdb)
        arcpy.Compact_management(gdb)
        arcpy.AddMessage("\t" + fileGDBname + " is compacted")
        print "\t" + fileGDBname + " is compacted"
    except:
        print arcpy.GetMessages
        arcpy.AddMessage("\n" + fileGDBname)
        print "\n" + fileGDBname
        arcpy.AddMessage("\t" + fileGDBname + " is locked")
        print "\t" + fileGDBname + " is locked"



# 2. List subfolders in workspace
subfolderList = arcpy.ListWorkspaces("*","Folder")
subfolderList.sort()

for subfolder in subfolderList:

        print "\n\t" + os.path.basename(subfolder) + " folder"
        arcpy.AddMessage("\n\t" + os.path.basename(subfolder) + " folder")
        arcpy.env.workspace = subfolder
        subgdbs = arcpy.ListWorkspaces("*","FileGDB")
        subgdbs.sort()

# List file GDBs in subfolders              
        for subgdb in subgdbs:

            try:
# Compact file gdbs in subfolders
                subGDBname = os.path.basename(subgdb)
                arcpy.Compact_management(subgdb)
                arcpy.AddMessage("\t\t" + subGDBname + " is compacted")
                print "\t\t" + subGDBname + " is compacted"
            except:
                print arcpy.GetMessages
                arcpy.AddMessage("\n" + subGDBname)
                print "\n" + subGDBname
                arcpy.AddMessage("\t" + subGDBname + " is locked")
                print "\t" + subGDBname + " is locked"



# 3. List subfolders in subfolders
        sub2folderList = arcpy.ListWorkspaces("*","Folder")
        sub2folderList.sort()

        for sub2folder in sub2folderList:

                print "\n\t\t" + os.path.basename(sub2folder) + " subfolder"
                arcpy.AddMessage("\n\t\t" + os.path.basename(sub2folder) + " subfolder")
                
                arcpy.env.workspace = sub2folder
                sub2gdbs = arcpy.ListWorkspaces("*","FileGDB")
                sub2gdbs.sort()

        # List file GDBs in subfolders              
                for sub2gdb in sub2gdbs:

                    try:
        # Compact file gdbs in subfolders
                        sub2GDBname = os.path.basename(sub2gdb)
                        arcpy.Compact_management(sub2gdb)
                        print "\t\t\t" + sub2GDBname + " is compacted"
                        arcpy.AddMessage("\t\t\t" + sub2GDBname + " is compacted")
                    except:
                        print arcpy.GetMessages
                        arcpy.AddMessage("\n" + sub2GDBname)
                        print "\n" + sub2GDBname
                        arcpy.AddMessage("\t" + sub2GDBname + " is locked")
                        print "\t" + sub2GDBname + " is locked"
                    

print datetime.datetime.now() - startTime         
print 'done'






