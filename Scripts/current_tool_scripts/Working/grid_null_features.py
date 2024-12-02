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

arcpy.env.workspace = r'E:\gpw\country\fishnets\Nulls'
workspaces = arcpy.ListWorkspaces("*","FILEGDB")
for workspace in workspaces:
    arcpy.env.workspace = workspace
    fcs = arcpy.ListFeatureClasses("*")
    fc = fcs[0]   
    print fc
    # Define inputs
    # Input ISOCODE
    fcString = os.path.basename(workspace)[:-4]
    fcString = fcString.upper()
    # Create Output Folder
    outputRoot = workspace
    outGDB = workspace

    # Define Workspace
    env.workspace = workspace
    # Project Data
    # Input Fishnet
    fish = workspace + os.path.sep + fcString + "_fishnet"
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
    gridFieldsWildCard = "*MASK*" #"*TOTPOPBT_2010*M""*CNTM"#
    gridFields = arcpy.ListFields(fish,gridFieldsWildCard)

    # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
    # 1 degree divided into 120 parts is 30 seconds
    linespd = 120 ## Update As Needed
    cellSize = 1.0 / linespd
    # Output the gridded count rasters
    for field in gridFields:
        gridField = field.name
        print "The field to be gridded is " + gridField
        arcpy.AddMessage("The field to be gridded is " + gridField)
        # Output Grids
        #+ os.path.sep + fcString + "_grids.gdb"
        if gridField[:3] == "SUM":
            gridName = gridField[4:]
        else:
            gridName = gridField 
        outGrid =  workspace + os.path.sep + fcString + "_" + gridName
        arcpy.env.extent = arcpy.Extent(-180,-60,180,85)
        arcpy.env.outputCoordinateSystem = wgs84
        arcpy.env.cellSize = cellSize
        print "The extent is " + str(arcpy.env.extent)
        arcpy.AddMessage("The extent is " + str(arcpy.env.extent))
        if arcpy.Exists(outGrid):
            arcpy.AddMessage(outGrid + " exists")
        else:
            try:
                arcpy.PolygonToRaster_conversion(fish,gridField,outGrid,'CELL_CENTER','#',cellSize)
                print "Created " + outGrid
                arcpy.AddMessage("Created " + outGrid)
            except:
                print arcpy.GetMessages()
                arcpy.AddMessage(arcpy.GetMessages())

