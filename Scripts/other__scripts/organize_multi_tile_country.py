# Kytt MacManus
# 3-13-14
# create GDBs and copy appropriate files for multi-tile countries

import arcpy
import os

# define workspace
## Update as Needed
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\grl_municipality\municipalities'

# define env.workspace
arcpy.env.workspace = workspace.replace("municipalities","grl_by_admin2.gdb")

# define estimates table
estimates = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\grl_municipality\grl.gdb\grl_estimates'
prefix = "grl_"
# create list of fcs
fcs = arcpy.ListFeatureClasses("*")
# iterate
for fc in fcs:
    print fc
    # parse output files
    outWS = workspace + os.sep + prefix + fc.lower() + ".gdb"
    outFC = outWS + os.sep + prefix + fc.lower() + "_boundaries_2010"
    outEstimates = outWS + os.sep + prefix + fc.lower() + "_estimates"
    # copy fc to outFC
    try:
        arcpy.CopyFeatures_management(fc,outFC)
        print "Created " + outFC
    except:
        print arcpy.GetMessages()

    # copy estimates table
    try:
        arcpy.Copy_management(estimates,outEstimates)
        print "Created " + outEstimates
    except:
        print arcpy.GetMessages()
    
    
