# Author:      Erin Doxsey-Whitfield
# Date:        Oct. 7, 2014

# Copy estimates tables from input gdb to \\Dataserver0\gpw\GPW4\Gridding\global\inputs\estimates_tables.gdb
# 

#-------------------------------------------------------------------------------

# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
arcpy.env.workspace = workspace


# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List File GDBs in workspace
gdbList = arcpy.ListWorkspaces("*","FileGDB")
gdbList.sort()

for gdb in gdbList:
    iso = os.path.basename(gdb)[:-4]
    arcpy.env.workspace = gdb
    print iso

# VAT currently has a GDB name of VATI, but file iso code of vcs (Vatican City State)
    if iso == "vati":
        iso = "vcs"
        print iso
    else:
        pass

    estimates = iso + "_estimates"
    out_gdb = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\estimates_tables.gdb'
    out_table = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\estimates_tables.gdb' + os.sep + estimates
    

    arcpy.Copy_management(estimates, out_table)
    print "Copied " + iso 

print "Done"







##for fc in fcList:
##    
### Parse ISO from the feature class name
##        isoName = os.path.basename(fc)[0:3]
##        iso = isoName.lower()
##        print iso
