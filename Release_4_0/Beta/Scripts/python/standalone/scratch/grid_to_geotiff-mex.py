# Kytt MacManus
# March 21 2014
# Convert GPW FGDB Grids to GeoTiff

# Import libraries
import arcpy, os, datetime

# Define workspace
gdb = r'D:\GPW\mex\mex.gdb'
# name of output directory
outputDir = r'D:\GPW\mex\tif'

# Set workspace environment
arcpy.env.workspace = gdb

# list grids
grids = arcpy.ListRasters("*")
# iterate
for grid in grids:
    procTime = datetime.datetime.now()
    print "Processing " + grid
##    year = grid.split("_")[3]
##    if grid.split("_")[4] == "CNTM":
##        suffix = "count"
##    else:
##        suffix = "density"
##    if grid.split("_")[2]=="ATOTPOPMT":
##        sex = "male"
##    else:
##        sex = "female"
    # copy grid to geotiff
    outTif = outputDir + os.sep + os.path.basename(grid) + ".tif"
    if arcpy.Exists(outTif):
        print outTif + " already exists"
    else:
        try:
            arcpy.CopyRaster_management(grid,outTif,"#","#",
                                        -407649103380480.000000,
                                        "NONE","NONE","32_BIT_FLOAT")
            print "Created " + outTif
            print str(datetime.datetime.now()-procTime)
        except:
            print arcpy.GetMessages()
                
