#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      edwhitfi
#
# Created:     27/07/2014
# Copyright:   (c) edwhitfi 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, os

##arcpy.env.workspace = r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Compaction\test_folder'
##arcpy.env.workspace = r'\\dataserver0\gpw\GPW4\Gridding\country\inputs'
arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\can_province\inputs'

# List file GDBs
gdbs = arcpy.ListWorkspaces("*","FileGDB")
gdbs.sort

for gdb in gdbs:

    try:
# Compact file gdb
        fileGDBname = os.path.basename(gdb)
        print fileGDBname
        arcpy.Compact_management(gdb)
        print "\t" + fileGDBname + " is compacted"
    except:
        print arcpy.GetMessages()
        print "\n" + fileGDBname
        print "\t" + fileGDBname + " is locked"
print 'done'

# \\Dataserver0\gpw\GPW4\Gridding\country\inputs
# Pre-compaction: 1.40 TB (Oct 29, 2014)
# Post-compaction of main folder and cleaning: 1.10 TB (Nov 3, 2014)
# Post-compaction of all subfolders: 760 GB (Nov 3, 2014)

