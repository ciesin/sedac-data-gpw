# GPW Gridding
# Purpose: To proportionally allocate demographic variables to grid cells * Adapted to support selections
# Kytt MacManus
# September 13, 2012

# Import Python Libraries
import arcpy, os, sys
from arcpy import env

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

# Set Overwrite Output Environment
env.overwriteOutput = 1

# Define Workspace Variable
workspace = r'D:\gpw4\ecu\ecu_output.gdb'

# Set Workspace and Scratch Workspace Environments
env.workspace = workspace
env.scratchworkspace = workspace

# Define input fc
fc = "ecu_admin3_inec_final"
# Define input census table
table = "ecu_2010_census"
sqlTable = "sqlTable"
# Define joinField
joinField = "UCADMIN3"

# Create copy of fc
fcCopy = "ecu_2010"
if arcpy.Exists(fcCopy) == False:
    try:
        arcpy.CopyFeatures_management(fc,fcCopy)
    except:
        print arcpy.GetMessages()
else:
    print fcCopy + " already exists"
fc = fcCopy
print "Processing " + fc
# Add population field
populationField = "POPTOTALBOTHTOTAL"
if check_for_field(fc,populationField):
    print "Population field exists in table...double check script"
else:
    arcpy.AddField_management(fc,populationField,'LONG')
    print "Added " + populationField
# Create Feature Layer of fc
fcLayer = "fcLayer"
try:
    arcpy.MakeFeatureLayer_management(fc,fcLayer)
except:
    print arcpy.GetMessages()
# Create Table View of Census Values with SQLQuey
try:
    sqlQuery = '"' + "Age" + '"' + " = 'TOTAL' AND " + '"' + "URDESIGNATION" + '"' + " = 'TOTAL' AND " + '"' + "MFDESIGNATION" + '"' + " = 'BOTH'"
    arcpy.MakeTableView_management(table,sqlTable,sqlQuery)
except:
    print arcpy.GetMessages()
# Add Join
try:
    arcpy.AddJoin_management(fcLayer,joinField,sqlTable,joinField,"KEEP_ALL")
except:
    print arcpy.GetMessages()
# Calculate field
calculationExpression = "[" + table + ".POPULATION]"
try:
    arcpy.CalculateField_management(fcLayer,populationField,calculationExpression)
except:
    print arcpy.GetMessages()
# Remove Join
try:
    arcpy.RemoveJoin_management(fcLayer)
except:
    print arcpy.GetMessages()
# Delete Views to free up memory
try:
    arcpy.Delete_management(sqlTable)
    arcpy.Delete_management(fcLayer)
except:
    print arcpy.GetMessages()

# Define Gridding Variables
gridFields = [populationField]## Update As Needed
# Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
# 1 degree divided into 120 parts is 30 seconds
linespd = 120 ## Update As Needed

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
# add a tmpid field and calculate it equal to the FID or OBJECTID
try:
    tmpid = "TEMPID"
    if check_for_field(fc,tmpid):
        arcpy.DeleteField_management(fc,tmpid)
        print "Deleted " + tmpid
        arcpy.AddField_management(fc,tmpid,'LONG','12')
        print "Added " + tmpid
    else:
        arcpy.AddField_management(fc,tmpid,'LONG','12')
        print "Added " + tmpid
except:
    print arcpy.GetMessages()
try:
    if check_for_field(fc,'FID'):
        print "The tempid is equal to the FID"
        arcpy.CalculateField_management(fc,tmpid,'[FID]')
    else:
        print "The tempid is equal to the OBJECTID"
        arcpy.CalculateField_management(fc,tmpid,'[OBJECTID]')       
except:
    print arcpy.GetMessages()

# Grab Projection Information from Global Mollweide
mollweide = arcpy.SpatialReference(54009)
# Export as string
mollweideString = mollweide.exportToString()
# Replace Central Meridian with xctr
mollweideOut = mollweideString.replace("['Central_Meridian',0.0]","['Central_Meridian'," + str(xctr) + "]")
# Load new string into spatial reference Object
mollweide.loadFromString(mollweideOut)
mollweideCustom = mollweide
print "The central meridian in the new projection is now " + str(mollweideCustom.centralMeridian)
# Project the fc to mollweideCustom
try:        
    outputFc = fc + '_projected'
    arcpy.Project_management(fc,outputFc,mollweideCustom)
    print "Projected " + fc
except:
    print arcpy.GetMessages()
# Add area field. If it already exists, delete and add again to be certain
# of the type. 
try:
    areaField = "AREASQKM"
    if check_for_field(fc,areaField):
        arcpy.DeleteField_management(fc,areaField)
        print "Deleted " + areaField
        arcpy.AddField_management(outputFc,areaField,'DOUBLE')
        print "Added " + areaField
    else:
        arcpy.AddField_management(outputFc,areaField,'DOUBLE')
        print "Added " + areaField
except:
    print arcpy.GetMessages()    
# Calculate the areaField
try:
    arcpy.CalculateField_management(outputFc,areaField,'!shape.area@SQUAREKILOMETERS!','PYTHON')
    print "Calculated " + areaField
except:
    print arcpy.GetMessages()
# Copy it over to the input fc
# Add indexes
try:
    arcpy.AddIndex_management(fc,tmpid,tmpid)
    arcpy.AddIndex_management(outputFc,tmpid,tmpid)
except:
    print arcpy.GetMessages()
try:        
    arcpy.JoinField_management(fc,tmpid,outputFc,tmpid,areaField)
    print "Joined " + areaField + " to " + fc
except:
    print arcpy.GetMessages()
### This section is adapted form calcdensities.py as written
### by Greg Yetman circa 2010
# Iterate through gridFields list
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
### This section is adapted form grid.py as written
### by Greg Yetman circa 2010
# Cell size is one degree divided by lines per degree
cellSize = 1.0 / linespd
# Expand fc extent to the nearest degree for processing area
xmin = int(round(extent.XMin - .5))
xmax = int(round(extent.XMax + .5))
ymin = int(round(extent.YMin - .5))
ymax = int(round(extent.YMax + .5))
# calc the number of rows and columns, corners, etc.
cellSizeWidth = cellSize
cellSizeHeight = cellSize
numRows = (ymax - ymin) * linespd
numCols = (xmax - xmin) * linespd
orgCoord = str(xmin) + ' ' + str(ymin)
oppCorner = str(xmax) + ' ' + str(ymax)
yaxisCoord = str(xmin) + " " + str(ymin + 10)
print 'Output grid has the following dimensions:'
print 'Xmin:', xmin
print 'YMin:', ymin
print 'XMax:', xmax
print 'YMax:', ymax
print 'Columns:', numCols
print 'Rows:   ', numRows
print 'Cell Size:   ', cellSize
print 'Origin Coordinate:   ', orgCoord
print 'Y Axis Coordinate:   ', yaxisCoord
print 'Opposite Corner:   ', oppCorner
# Calculate Fishnet
print 'Generating fishnet for input feature class'
fish = env.workspace + os.sep + fc + "_fishnet"
wgs84 = arcpy.SpatialReference(4326)
try:
    arcpy.CreateFishnet_management(fish,orgCoord,str(yaxisCoord),cellSizeWidth,cellSizeHeight,
                               numRows,numCols,'#','NO_LABELS',fc,'POLYGON')
    arcpy.DefineProjection_management(fish,wgs84)
    print "Created " + fish
except:
    print arcpy.GetMessages()
# Add a unique id field
uid = "UID"
try:
    arcpy.AddField_management(fish,uid,'LONG')
    print "Added " + uid
except:
    print arcpy.GetMessages()
# Calculate the Unique id
try:
    arcpy.CalculateField_management(fish,uid,'!OID!','PYTHON')
    print "Calculated " + uid
except:
    print arcpy.GetMessages()
# clip the fishnet to the input fc extent        
clipnet = "in_memory" + os.sep + fc + "_fishnet_clipped"
try:
    arcpy.Clip_analysis(fish,fc,clipnet)
    print 'Clipping fishnet to input feature class', fc
except:
    print arcpy.GetMessages()
# Intersect Fishnet and FC
clipnetInt = env.workspace + os.sep + fc + "_fishnet_clipped_intersect"
inFeatures = [fc,clipnet]
try:
    arcpy.Intersect_analysis(inFeatures, clipnetInt)
    print 'Intersected clipped fishnet and input features.'
except:
    print arcpy.GetMessages()
# Add another Unique ID Field called INTRSCTID
INTRSCTID = "INTRSCTID"
try:
    arcpy.AddField_management(clipnetInt,INTRSCTID,'LONG')
    print "Added " + INTRSCTID
except:
    print arcpy.GetMessages()
# Calculate the Unique INTRSCTID
try:
    arcpy.CalculateField_management(clipnetInt,INTRSCTID,'!OBJECTID!','PYTHON')
    print "Calculated " + uid
except:
    print arcpy.GetMessages()
# Project clipnetInt to mollweideCustom
try:        
    outputClipnetInt = clipnetInt + '_projected'
    arcpy.Project_management(clipnetInt,outputClipnetInt,mollweideCustom)
    print "Projected " + clipnetInt
except:
    print arcpy.GetMessages()
# Add area field. If it already exists, delete and add again to be certain
# of the type. 
try:
    areaFieldInt = "AREASQKMINT"
    if check_for_field(outputClipnetInt,areaFieldInt):
        arcpy.DeleteField_management(outputClipnetInt,areaFieldInt)
        print "Deleted " + areaFieldInt
        arcpy.AddField_management(outputClipnetInt,areaFieldInt,'DOUBLE')
        print "Added " + areaFieldInt
    else:
        arcpy.AddField_management(outputClipnetInt,areaFieldInt,'DOUBLE')
        print "Added " + areaFieldInt
except:
    print arcpy.GetMessages()    
# Calculate the areaField
try:
    arcpy.CalculateField_management(outputClipnetInt,areaFieldInt,'!shape.area@SQUAREKILOMETERS!','PYTHON')
    print "Calculated " + areaFieldInt
except:
    print arcpy.GetMessages()
# Copy it over to the clipnetInt
# Add indexes
try:
    arcpy.AddIndex_management(clipnetInt,INTRSCTID,INTRSCTID)
    arcpy.AddIndex_management(outputClipnetInt,INTRSCTID,INTRSCTID)
except:
    print arcpy.GetMessages()
try:        
    arcpy.JoinField_management(clipnetInt,INTRSCTID,outputClipnetInt,INTRSCTID,areaFieldInt)
    print "Joined " + areaFieldInt + " to " + clipnetInt
except:
    print arcpy.GetMessages()
# Total population per fishnet/fc intersection using proportional allocation
print 'Calculating proprotional share of density items in intersection output.'
cntFields = [[areaFieldInt,'SUM']]
for field in gridFields:
    gridField = field + "_DS"
    newField = field + "_CNT"
    cntFields.append([newField, 'SUM'])
    try:
        arcpy.AddField_management(clipnetInt,newField,'Double')
        print "Added " + newField
    except:
        print arcpy.GetMessages()
    try:
        arcpy.CalculateField_management(clipnetInt,newField,"!" + areaFieldInt + "! * !" + gridField + "!","PYTHON")
        print "Calculated Population in " + newField
    except:
        print arcpy.GetMessages()
# Sum proportional allocation count fields and join to original fishnet
sumTbl = fc + "_sumTbl"#"in_memory" + os.sep + fc + "_sumTbl"
try:
    arcpy.Statistics_analysis(clipnetInt,sumTbl,cntFields,uid)
    print "Calculate Statistics"
except:
    print arcpy.GetMessages()
# Join results to original fishnet
# Add indexes
try:
    arcpy.AddIndex_management(fish,uid,uid)
    arcpy.AddIndex_management(sumTbl,uid,uid)
except:
    print arcpy.GetMessages()
try:
    arcpy.JoinField_management(fish,uid,sumTbl,uid)
    print "Joined Statistic Fields to " + fish
except:
    print arcpy.GetMessages()
# Output the land area raster           
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
### Delete temp grids
##try:
##    arcpy.Delete_management(outputFc)
##    print "Deleted " + outputFc
##    arcpy.Delete_management(outputClipnetInt)
##    print "Deleted " + outputClipnetInt
##except:
##    print arcpy.GetMessages()
