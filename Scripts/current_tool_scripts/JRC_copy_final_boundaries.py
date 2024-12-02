# This script copies the final boundaries for JRC to the final GDB



# Import Libraries
import arcpy, os, csv
from arcpy import env
import datetime
startTime = datetime.datetime.now()

# Define Workspace Variable
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\gridding_gdb_for_JRC\intermediary_files'
workspace = r'\\Dataserver0\gpw\GPW4\MISC\GPW data for others\JRC_GHSLwork\intermediary_files'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

#iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    # Parse ISO
    iso = os.path.basename(gdb)[:-4]
    print iso

 # Copy jrc bounary final GDB

    jrc_boundarys = arcpy.ListFeatureClasses("*jrc")
    for jrc_boundary in jrc_boundarys:

        out_gdb = r'\\Dataserver0\gpw\GPW4\MISC\GPW data for others\JRC_GHSLwork\Final_data_sent\JRC_gpwv4_data.gdb'
        out_data = out_gdb + os.sep + jrc_boundary

        arcpy.Copy_management(jrc_boundary, out_data)
        print "\t" + jrc_boundary + " copied"


print "done"
        
