# Kytt MacManus
# July 24 2014
# Copy Grids to 

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
outRoot = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters_v4.0_alpha2'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*_grids.gdb","FILEGDB")
gdbs.sort()

# iterate
for gdb in gdbs:
    print gdb
    arcpy.env.workspace = gdb
    # Parse COUNTRYCODE
    COUNTRYCODE = os.path.basename(gdb)[:-10].upper()
    wildcards = ["*numinputs*"]#,"*_E_*ATOTPOPBT*2010*"]["*area*"]
    for wildcard in wildcards:
        # list rasters
        rasters = arcpy.ListRasters(wildcard)
        for raster in rasters:
            # parse variable name
            variable = raster[4:]
            # define out gdb
            outGDB = outRoot + os.sep + variable + ".gdb"
            # if outGDB does not exist, then create it
            if not arcpy.Exists(outGDB):
                arcpy.CreateFileGDB_management(outRoot,variable)
                print "Created " + outGDB
            else:
                pass    
            inRaster = raster
            # Parse output Raster
            outRaster = outGDB + os.sep + COUNTRYCODE + "_" +variable
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
