# Kytt MacManus
# Calculate Density

# Import libraries
import arcpy, os, datetime

# Define workspace
workspace = r'D:\gpw\release_4_1\gdal_tifs'

# Set workspace environment
arcpy.env.workspace = workspace

# Check out Spatial Analyst License
arcpy.CheckOutExtension("SPATIAL")
# List File GDBs
rasters = arcpy.ListRasters("*count*")
outWS = r'D:\gpw\release_4_1\merge'
# Iterate
for raster in rasters:
    print "processing " + raster
    procTime = datetime.datetime.now()
    outDens = outWS + os.sep + os.path.basename(raster).replace("population-count","population-density")
    area = r"D:\gpw\release_4_1\global_tifs\GPW4rev10_LANDAREAKM.tif"
    try:
        density = arcpy.sa.Divide(raster,area)
        density.save(outDens)
        arcpy.BuildPyramidsandStatistics_management(outDens)
        print "Created " + outDens
        print str(datetime.datetime.now()-procTime)
    except:
        print arcpy.GetMessages()
