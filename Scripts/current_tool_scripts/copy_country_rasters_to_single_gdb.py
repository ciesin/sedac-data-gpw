# Kytt MacManus
# July 24 2014
# Copy Grids to 

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
outGDB = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters\UNE_ATOTPOPBT_2000_CNTM.gdb'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*_grids.gdb","FILEGDB")
gdbs.sort()
# Define ListRasters Wildcard
wildCard = "_UNE_ATOTPOPBT_2000_CNTM"
# iterate
for gdb in gdbs:
    # Parse COUNTRYCODE
    COUNTRYCODE = os.path.basename(gdb)[:-10].upper()
    # Parse input Raster
    inRaster = gdb + os.sep + COUNTRYCODE + wildCard
    # Parse output Raster
    outRaster = outGDB + os.sep + COUNTRYCODE + wildCard
    if not arcpy.Exists(inRaster):
        inRaster = gdb + os.sep + COUNTRYCODE + wildCard[2:]
        outRaster = outGDB + os.sep + COUNTRYCODE + wildCard[2:]
    # Copy Raster
    if not arcpy.Exists(outRaster):
        try:
            arcpy.CopyRaster_management(inRaster,outRaster)
            print "Created " + outRaster
            arcpy.AddMessage("Created " + outRaster)
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
    else:
        print outRaster + " already exists"
   
                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
