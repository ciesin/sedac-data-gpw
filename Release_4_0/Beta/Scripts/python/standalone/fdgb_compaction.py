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
arcpy.env.workspace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\fishnets_and_clipped_water\can'

# List file GDBs
gdbs = arcpy.ListWorkspaces("*","FileGDB")
gdbs.sort()

for gdb in gdbs:
    print gdb
    try:
# Compact file gdb
        fileGDBname = os.path.basename(gdb)
        arcpy.Compact_management(gdb)
        print "\t" + fileGDBname + " is compacted"
    except:
        print arcpy.GetMessages()
        print "\n" + fileGDBname
        print "\t" + fileGDBname + " is locked"
print 'done'



