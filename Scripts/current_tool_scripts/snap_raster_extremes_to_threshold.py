# Kytt MacManus
# 11-4-14
# Snap Raster Extremes to Threshold

# import libraries
import arcpy, os, datetime
# set script timer
startTime = datetime.datetime.now()
# check out SPATIAL extension
arcpy.CheckOutExtension("SPATIAL")
# define input raster
##rasterIn = arcpy.GetParameterAsText(0)
inRaster = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters_v4.0_alpha2\merged\global_grids.gdb\GL_AREAKM_v0'
# create boolean parameter to allow user ability to save intermediate data to a scratch workspace
##saveIntermediate = arcpy.GetParameterAsText(1)
saveIntermediate = "true"
# define optional scratch workspace to store intermediate data
##scratchWorkspace = arcpy.GetParameterAsText(2)
scratchWorkspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters_v4.0_alpha2\merged\scratch'
# define intermediate files
reclassRaster = scratchWorkspace + os.sep + os.path.basename(inRaster) + "_reclass.tif"
# define classification threshold
##classThreshold = arcpy.GetParameterAsText(3)
classThreshold = "0.85857266187668"
# define raster of replacement values
##falseRaster = arcpy.GetParameterAsText(4)
falseRaster = r'\\Dataserver0\gpw\GPW4\Gridding\global\ancillary\global_30_second_surface_area.tif'
# define output raster
##rasterOut = arcpy.GetParameterAsText(5)
outRaster = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters_v4.0_alpha2\merged\global_grids.gdb\GL_AREAKM'
# start processing
# consider input raster and determine is maximum value
# GetRasterProperties is dependent on the raster having statistics calculated
# if inRaster doesn't have statistics then calculate them
try:
    maxRasterValue = arcpy.GetRasterProperties_management(inRaster, "MAXIMUM").getOutput(0)
except:
    arcpy.CalculateStatistics_management(inRaster)
    maxRasterValue = arcpy.GetRasterProperties_management(inRaster, "MAXIMUM").getOutput(0)
print "The maximum value in " + inRaster + " is: " + maxRasterValue
arcpy.AddMessage("The maximum value in " + inRaster + " is: " + maxRasterValue)
# parse the remapRange
remapRange = arcpy.sa.RemapRange([[0,classThreshold,1],[classThreshold,maxRasterValue,2]])
# define mask raster
arcpy.env.mask = inRaster
# execute reclassification
try:
    processTime = datetime.datetime.now()
    reclass = arcpy.sa.Reclassify(inRaster,"Value",remapRange,"NODATA")
    reclass.save(reclassRaster)
    print "Created " + reclassRaster + " in: " + str(datetime.datetime.now() - processTime)
    arcpy.AddMessage("Created " + reclassRaster + " in: " + str(datetime.datetime.now() - processTime))
except:
    print arcpy.GetMessages()
    arcpy.AddMessage(arcpy.GetMessages())
# execute con statement to produce outRaster
try:
    processTime = datetime.datetime.now()
    con = arcpy.sa.Con(arcpy.sa.Raster(reclassRaster)==1,arcpy.sa.Raster(inRaster),arcpy.sa.Raster(falseRaster))
    con.save(outRaster)
    print "Created " + outRaster + " in: " + str(datetime.datetime.now() - processTime)
    arcpy.AddMessage("Created " + outRaster + " in: " + str(datetime.datetime.now() - processTime))
except:
    print arcpy.GetMessages()
    arcpy.AddMessage(arcpy.GetMessages())

print "Script executed in: " + str(datetime.datetime.now() - startTime)
arcpy.AddMessage("Script executed in: " + str(datetime.datetime.now() - startTime))








    
