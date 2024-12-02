# GPW Gridding
# Purpose: To grid  fishnet variables via WPS 
# Kytt MacManus
# March 4, 2013

# Import Python Libraries
import arcpy, os, string
from arcpy import env

# Set Overwrite Output Environment
env.overwriteOutput = True

# helper method to check if a field exists in a fc
def check_for_field(featClass,fieldName):
    hasField = 0
    desc = arcpy.Describe(featClass)
    fields = desc.fields
    for field in fields:
        # check without case as ArcGIS is not case sensitive
        if field.name.upper() == fieldName:
            hasField = 1    
    return hasField

# Define inputs
# Input ISOCODE
fcString ="GMB" #arcpy.GetParameterAsText(0)
fcString = fcString.upper()
# Define Workspace
env.workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs' + os.sep + fcString + ".gdb"
# Create Output Folder
outputRoot = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
outGDB = fcString + "_rasters"
outputFolder = outputRoot + outGDB + ".gdb"
if not arcpy.Exists(outputFolder):
    arcpy.


# Project Data
# Input Fishnet
fish = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs' + os.sep + fcString + ".gdb" + os.path.sep + fcString + "_fishnet"
# Coordinate System
wgs84 = arcpy.SpatialReference(4326)
# Describe Fish
desc = arcpy.Describe(fish)
# Calculate Raster Extent
extent = desc.Extent
xmin = int(round(extent.XMin - .5))
xmax = int(round(extent.XMax + .5))
ymin = int(round(extent.YMin - .5))
ymax = int(round(extent.YMax + .5))

# Define Gridding Variables
gridFieldsWildCard = "*M" #arcpy.GetParameter(1)#"*TOTPOPBT_2010*M"
gridFields = arcpy.ListFields(fish,gridFieldsWildCard)

# Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
# 1 degree divided into 120 parts is 30 seconds
linespd = 120 ## Update As Needed
cellSize = 1.0 / linespd
# Output the gridded count rasters
for field in gridFields:
    gridField = field.name
    arcpy.AddMessage("The field to be gridded is " + gridField)
    # Output Grids
    #+ os.path.sep + fcString + "_grids.gdb"
    if gridField[:3] == "SUM":
        gridName = gridField[4:]
    else:
        gridName = gridField
    outPopGrid =  outputFolder  + os.path.sep + fcString + "_" + gridField
    arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
    arcpy.env.outputCoordinateSystem = wgs84
    arcpy.env.cellSize = cellSize
    arcpy.AddMessage("The extent is " + str(arcpy.env.extent))
    if arcpy.Exists(outPopGrid):
        arcpy.AddMessage(outPopGrid + " exists")
    else:
        try:
            arcpy.PolygonToRaster_conversion(fish,gridField,outPopGrid,'CELL_CENTER','#',cellSize)
            copy = r"E:\arcserver\data\tooldata" + os.path.sep + fcString + "_grids.gdb" + os.path.sep + fcString + "_" + gridName
            arcpy.CopyRaster_management(outPopGrid,copy)
            arcpy.AddMessage("Created " + outPopGrid)
        except:
            arcpy.AddMessage(arcpy.GetMessages())
