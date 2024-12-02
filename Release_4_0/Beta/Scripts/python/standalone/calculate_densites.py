# Kytt MacManus
# Calculate Density

# Import libraries
import arcpy, os, datetime

# Define workspace
workspace = r'F:\gpw\global\gpw4.gdb'

# Set workspace environment
arcpy.env.workspace = workspace

# Check out Spatial Analyst License
arcpy.CheckOutExtension("SPATIAL")
# List File GDBs
rasters = arcpy.ListRasters("*MT*")

# Iterate
for raster in rasters:
    print "processing " + raster
    procTime = datetime.datetime.now()
    outDens = workspace + os.sep + os.path.basename(raster).replace("CNTM","DENS")
    area = workspace + os.sep + "GL_AREAKMMASKED"
    try:
        density = arcpy.sa.Divide(raster,area)
        density.save(outDens)
        arcpy.BuildPyramidsandStatistics_management(outDens)
        print "Created " + outDens
        print str(datetime.datetime.now()-procTime)
    except:
        print arcpy.GetMessages()
