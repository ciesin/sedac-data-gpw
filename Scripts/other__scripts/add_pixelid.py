# Kytt MacManus
# 3-13-14
# create GDBs and copy appropriate files for multi-tile countries

import arcpy
import os

# define workspace
## Update as Needed
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\grl_municipality\municipalities'

# define env.workspace
arcpy.env.workspace = workspace

# list gdbs
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
for gdb in gdbs:
    prefix = os.path.basename(gdb)[:-4]
    fishnet = gdb + os.sep + prefix + "_fishnet"
    arcpy.AddField_management(fishnet,"PIXELID","LONG")
    arcpy.CalculateField_management(fishnet,"PIXELID","!grid_code!","PYTHON")
    print "Calculated PixelID for " + prefix
    
