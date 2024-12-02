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

##arcpy.env.workspace = r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Compaction\test_folder'
arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\grl_municipality'



# List subfolders
subfolderList = arcpy.ListWorkspaces("*","Folder")
subfolderList.sort()

for subfolder in subfolderList:

        print os.path.basename(subfolder)
        arcpy.env.workspace = subfolder
        subgdbs = arcpy.ListWorkspaces("*","FileGDB")
        subgdbs.sort()

# List file GDBs in subfolders              
        for subgdb in subgdbs:

            try:
# Compact file gdbs in subfolders
                fileGDBname = os.path.basename(subgdb)
                print fileGDBname
                arcpy.Compact_management(subgdb)
                print "\t" + fileGDBname + " is compacted"
            except:
                print arcpy.GetMessages
                print "\n" + fileGDBname
                print "\t" + fileGDBname + " is locked"

            
# List file GDBs
arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\grl_municipality'

gdbs = arcpy.ListWorkspaces("*","FileGDB")

for gdb in gdbs:

    try:
# Compact file gdb
        fileGDBname = os.path.basename(gdb)
        print fileGDBname
        arcpy.Compact_management(gdb)
        print "\t" + fileGDBname + " is compacted"
    except:
        print arcpy.GetMessages
        print "\n" + fileGDBname
        print "\t" + fileGDBname + " is locked"
print 'done'






