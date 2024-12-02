# GPW Gridding
# Purpose: To proportionally allocate demographic variables to grid cells
# Kytt MacManus
# August 23, 2012

# Import Python Libraries
import arcpy, os
from arcpy import env

# Set Overwrite Output Environment
env.overwriteOutput = 1

# Define Workspace Variable
workspace = r'D:\gpw4\bmu\BMU.gdb'

# Set Workspace and Scratch Workspace Environments
env.workspace = workspace
env.scratchworkspace = workspace

# Define input fc
fc = "bmu_2010"
fish = fc + "_fishnet"

# Define Gridding Variables
gridFields = ["A0_4","A5_9","A10_14","A15_19","A20_24","A25_29","A30_34","A35_39","A40_44",
              "A45_49","A50_54","A55_59","A60_64","A65_69","A70_74","A75_79","A80_84",
              "A85plus","A_TOTMT", "A_TOTFT", "A0_4MT", "A0_4FT", "A5_9MT", "A5_9FT",
              "A10_14MT", "A10_14FT", "A15_19MT", "A15_19FT", "A20_24MT", "A20_24FT", "A25_29MT",
              "A25_29FT", "A30_34MT", "A30_34FT", "A35_39MT", "A35_39FT", "A40_44MT", "A40_44FT",
              "A45_49MT", "A45_49FT", "A50_54MT", "A50_54FT", "A55_59MT", "A55_59FT", "A60_64MT",
              "A60_64FT", "A65_69MT", "A65_69FT", "A70_74MT", "A70_74FT", "A75_79MT", "A75_79FT",
              "A80_84MT", "A80_84FT", "A85plusMT", "A85plusFT"] ## Update As Needed
# Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
# 1 degree divided into 120 parts is 30 seconds
linespd = 120 ## Update As Needed
areaField = "AREASQKM"

# Add a unique id field
uid = "UID"

# Intersected Fishnet 
clipnetInt = env.workspace + os.sep + fc + "_fishnet_clipped_intersect"


# helper method to check if a field exists in a fc
def check_for_field(featClass,fieldName):
    hasField = 0
    desc = arcpy.Describe(featClass)
    fields = desc.fields
    for field in fields:
        # check without case as ArcGIS is not case sensitive
        if field.name.upper() == fieldName.upper():
            hasField = 1
    return hasField


print "Processing " + fc
# Cell size is one degree divided by lines per degree
cellSize = 1.0 / linespd
### This section is adapted form calcareas.py as written
### by Greg Yetman circa 2010
# Error catch: make sure it is a featureclass, type = polygon, and is in WGS84
desc = arcpy.Describe(fc)
if desc.dataType != 'FeatureClass':
    print 'Input data type is not a feature class!'
    raise Exception()
else:
    pass
if desc.shapeType != 'Polygon':
    print 'Input feature class must be a polygon feature class'
    raise Exception()
else:
    pass
spatialRef = desc.spatialReference.name
if spatialRef != 'GCS_WGS_1984':
    print 'Input feature class projection undefined or not WGS84!'
    raise Exception()
else:
    pass
# Determine the Central Meridian of fc
extent = desc.Extent
# print ext.XMin, ext.Ymin, ext.Xmax, ext.Ymax
xctr = round(((extent.XMax + extent.XMin) / 2.0), 1)
print 'Central Meridian of', fc, 'is', xctr
# add a warning if range is greater than 180, it may cross hemispheres
if abs(extent.XMax - extent.XMin) > 180.0:
    print 'WARNING, input fc may cross 180 degrees E-W.'
    print 'If so, the central meridian could be misplaced and impact area calculations.'
else:
    pass  
# Expand fc extent to the nearest degree for processing area
xmin = int(round(extent.XMin - .5))
xmax = int(round(extent.XMax + .5))
ymin = int(round(extent.YMin - .5))
ymax = int(round(extent.YMax + .5))
### This section is adapted form calcdensities.py as written
### by Greg Yetman circa 2010
# Iterate through gridFields list
dsFields = []
for gridField in gridFields:
    # Check that the field exists
    skip = 0        
    if not check_for_field(fc, gridField):
        print "Numerator field " + gridField + " does not exist, skipping."
        skip = 1
    # check that the output field does not already exist, delete it if it does
    # and then add it
    if not skip:
        print "Calculating densities for " + gridField
        dsField = gridField + '_DS'
        areaFieldInt = "AREASQKMINT"        
        if check_for_field(fc,dsField):					
            try:
                arcpy.DeleteField_management(fc,dsField)
                print "Deleted " + dsField
            except:
                print arcpy.GetMessages()
            try:
                arcpy.AddField_management(fc,dsField,'DOUBLE')
                print "Added field: " + dsField
            except:
                print arcpy.GetMessages()
        else:
            try:
                arcpy.AddField_management(fc,dsField,'DOUBLE')
                print "Added field: " + dsField
            except:
                print arcpy.GetMessages()
        # Create a table view to avoid division by zero
        tblSel = 'tblSel'
        whereCls = areaField + ' > 0'
        tblSel = arcpy.MakeTableView_management(fc,tblSel,whereCls)
        # do the division
        exp = '!' + gridField + '! / !' + areaField + '!'
        try:
            arcpy.CalculateField_management(tblSel,dsField,exp,'PYTHON')
            print "Calculated " + dsField
        except:
            print arcpy.GetMessages()
        dsFields.append(dsField)
# Join DS Fields to clipnetInt by TEMPID
try:
    arcpy.JoinField_management(clipnetInt,"TEMPID",fc,"TEMPID",dsFields)
    print "Joined " + str(dsFields) + " to " + clipnetInt
except:
    print arcpy.GetMessages()

# Iterate through gridFields list
cntFields = [[areaFieldInt,'SUM']]
for gridField in gridFields:
    dsField = gridField + '_DS'
    cntField = gridField + "_CNT"
    cntFields.append([cntField, 'SUM'])
    # Total population per fishnet/fc intersection using proportional allocation
    print 'Calculating proprotional share of density items in intersection output.'    
    try:
        arcpy.AddField_management(clipnetInt,cntField,'Double')
        print "Added " + cntField
    except:
        print arcpy.GetMessages()
    try:
        arcpy.CalculateField_management(clipnetInt,cntField,"!" + areaFieldInt + "! * !" + dsField + "!","PYTHON")
        print "Calculated Population in " + cntField
    except:
        print arcpy.GetMessages()
# Sum proportional allocation count fields and join to original fishnet
sumTbl = env.workspace + os.sep + fc + "_sumTblAdditional"
try:
    arcpy.Statistics_analysis(clipnetInt,sumTbl,cntFields,uid)
    print "Calculated Statistics"
except:
    print arcpy.GetMessages()
# Join results to original fishnet
try:
    arcpy.JoinField_management(fish,uid,sumTbl,uid)
    print "Joined Statistic Fields to " + fish
except:
    print arcpy.GetMessages()
# Output the land area raster
wgs84 = arcpy.SpatialReference(4326)
outLandArea = env.workspace + os.sep + fc + '_LANDAREA'
arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
arcpy.env.outputCoordinateSystem = wgs84
arcpy.env.cellSize = cellSize
print "The extent is " + str(arcpy.env.extent)
if arcpy.Exists(outLandArea):
    print outLandArea + " exists"
else:
    try:
        arcpy.PolygonToRaster_conversion(fish,"sum_" + areaFieldInt,outLandArea,'CELL_CENTER','#',cellSize)
        print "Created " + outLandArea
    except:
        print arcpy.GetMessages()
# Output the gridded count rasters
for field in gridFields:
    gridField = "sum_" + field + '_CNT'
    print "The field to be gridded is " + gridField
    outPopGrid = env.workspace + os.sep + fc + "_" + field + "_COUNT"
    arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
    arcpy.env.outputCoordinateSystem = wgs84
    arcpy.env.cellSize = cellSize
    print "The extent is " + str(arcpy.env.extent)
    if arcpy.Exists(outPopGrid):
        print outPopGrid + " exists"
    else:
        try:
            arcpy.PolygonToRaster_conversion(fish,gridField,outPopGrid,'CELL_CENTER','#',cellSize)
            print "Created " + outPopGrid
        except:
            print arcpy.GetMessages()
