# Kytt MacManus
# Calculate Density

# Import libraries
import arcpy, os, datetime

# Define workspace
workspace = r'D:\gpw\4_0_prod\outTifs'

# Set workspace environment
arcpy.env.workspace = workspace

# Check out Spatial Analyst License
arcpy.CheckOutExtension("SPATIAL")
# List File GDBs
rasters = arcpy.ListRasters("*count*")

# Iterate
for raster in rasters:
    print "processing " + raster
    procTime = datetime.datetime.now()
    outDens = workspace + os.sep + os.path.basename(raster).replace("population-count","population-density")
    area = r"D:\gpw\4_0_prod\outTifs\gpw-v4-land-water-area_land.tif"
    try:
        density = arcpy.sa.Divide(raster,area)
        density.save(outDens)
        arcpy.BuildPyramidsandStatistics_management(outDens)
        print "Created " + outDens
        print str(datetime.datetime.now()-procTime)
    except:
        print arcpy.GetMessages()
