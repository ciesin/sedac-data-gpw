# GPW Adjust Geometries to Framework
# Purpose: To Adjust Geometries to Match GADM International Boundary and Coastline
# Kytt MacManus
# September 7, 2012

# Edited in September 2013 to add the calculation of QA statistics and export of suspect units

# Import Python Libraries
import arcpy, os, sys, datetime
from arcpy import env

# Set Overwrite Output Environment
env.overwriteOutput = 1
startTime = datetime.datetime.now()
# helper method to check if a field exists in a fc - by Greg Yetman
def check_for_field(featClass,fieldName):
    hasField = 0
    desc = arcpy.Describe(featClass)
    fields = desc.fields
    for field in fields:
        # check without case as ArcGIS is not case sensitive
        if field.name.upper() == fieldName.upper():
            hasField = 1
    return hasField
   
# Define workspace
##workspace = arcpy.GetParameterAsText(0)
workspace = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\CHL\Ingest\Boundary\boundary_adjustment.gdb'
env.workspace = workspace

# Define Framework Boundaries
##frameworkBoundaries =  arcpy.GetParameterAsText(1)
frameworkBoundaries = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\CHL\Ingest\Boundary\boundary_adjustment.gdb\CHL_admin0'
#arcpy.GetParameterAsText(0)
#"D:\gpw4\ecu\ecu_boundaries.gdb\ecu_admin3_gadm2_mainland" ## ON ACADIA Because Add Field doesn't work over network
#r"\\DATASERVER0\gpw\GPW4\Working\Merge\ECU\staging\ecu_boundaries.gdb\ecu_admin3_gadm2_mainland"

# Define Input boundaries
##inputBoundaries = arcpy.GetParameterAsText(2)
inputBoundaries = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\CHL\Ingest\Boundary\boundary_adjustment.gdb\com_chl'
#arcpy.GetParameterAsText(1)
#"D:\gpw4\ecu\ecu_boundaries.gdb\ecu_admin3_inec_mainland"
#r"\\DATASERVER0\gpw\GPW4\Working\Merge\ECU\staging\ecu_boundaries.gdb\ecu_admin3_inec_mainland"

# getCount of Input Boundary Features
inputCount = arcpy.GetCount_management(inputBoundaries)

# Create Framework ID and Calculate it
FRAMEWORKID = "INPUTID"
try:
    if check_for_field(inputBoundaries,FRAMEWORKID)==0:
        arcpy.AddField_management(inputBoundaries,FRAMEWORKID,"LONG")
        print "Added FRAMEWORKID"
        arcpy.AddMessage("Added FRAMEWORKID")
    else:
        arcpy.AddMessage("FRAMEWORKID Already exists")
    arcpy.CalculateField_management(inputBoundaries,FRAMEWORKID,"!" + "OBJECTID" +"!","PYTHON")
    print "Calculated FRAMEWORKID"
    arcpy.AddMessage("Calculated FRAMEWORKID")
except:
    arcpy.GetMessages()
# Define Area Check Fields
origArea = "ORIGAREA"
clipArea = "CLIPAREA"
clipAreaDiff = "CLIPAREAPCTDIFF"
finalArea = "FINALAREA"
finalAreaDiff = "FINALAREAPCTDIFF"
newFields = [origArea,clipArea,clipAreaDiff,finalArea,finalAreaDiff]
for newField in newFields:
    # If the field doesn't exist, then add it
    try:
        if check_for_field(inputBoundaries,newField)==0:
            arcpy.AddField_management(inputBoundaries,newField,'DOUBLE')
            print "Added " + newField
            arcpy.AddMessage("Added " + newField)
        else:
            print newField + " already exists"
            arcpy.AddMessage(newField + " already exists")
    except:
        print arcpy.GetMessages()
# Calculate ORIGAREA
try:
    if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(inputBoundaries,"inputLyr1",'"' + "ORIGAREA" + '"' + " IS NOT NULL"))[0])==0:
        arcpy.CalculateField_management(inputBoundaries,origArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        print "Calculated " + origArea
        arcpy.AddMessage("Calculated " + origArea)
    else:
        print origArea + " has already been calculated in " + os.path.basename(inputBoundaries)
        arcpy.AddMessage(origArea + " has already been calculated in " + os.path.basename(inputBoundaries))
except:
    arcpy.GetMessages()
                    
# Clip Input Boundaries to Framework Boundaries
clipBoundaries = inputBoundaries + "_clip"
if arcpy.Exists(clipBoundaries):
    print clipBoundaries + " already exists"
    arcpy.AddMessage(clipBoundaries + " already exists")
else:
    try:
        arcpy.Clip_analysis(inputBoundaries,frameworkBoundaries,clipBoundaries)
        print "Created " + clipBoundaries
        arcpy.AddMessage("Created " + clipBoundaries)
    except:
        arcpy.GetMessages()
# Calculate CLIPAREA
try:
    if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(clipBoundaries,"clipLyr1",'"' + "CLIPAREA" + '"' + " IS NOT NULL"))[0])==0:
        arcpy.CalculateField_management(clipBoundaries,clipArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        print "Calculated " + clipArea
        arcpy.AddMessage("Calculated " + clipArea)
    else:
        print clipArea + " has already been calculated in " + os.path.basename(inputBoundaries)
        arcpy.AddMessage(clipArea + " has already been calculated in " + os.path.basename(clipBoundaries))
except:
    arcpy.GetMessages()

# Find symmetrical difference of clipBoundaries and frameworkBoundaries
symBoundaries = clipBoundaries + "_symdiff"
if arcpy.Exists(symBoundaries):
    arcpy.AddMessage(symBoundaries + " already exists")
    print symBoundaries + " already exists"
else:
    try:
        arcpy.SymDiff_analysis(clipBoundaries,frameworkBoundaries,symBoundaries,
                               "ALL")
        arcpy.AddMessage("Created " + symBoundaries)
        print "Created " + symBoundaries
    except:
        print arcpy.GetMessages()

# Create Clip ID and Calculate it
CLIPID = "CLIPID"
try:
    if check_for_field(clipBoundaries,CLIPID)==0:
        arcpy.AddField_management(clipBoundaries,CLIPID,"LONG")
        arcpy.AddMessage("Added CLIPID")
        print "Added CLIPID"
    else:
        arcpy.AddMessage("CLIPID Already exists")
        print "CLIPID Already exists"
    arcpy.CalculateField_management(clipBoundaries,CLIPID,"!" + "OBJECTID" +"!","PYTHON")
    arcpy.AddMessage("Calculated CLIPID")
    print "Calculated CLIPID"
except:
    arcpy.AddMessage(arcpy.GetMessages())
       
# Create 30 arc second fishnet
# Describe frameworkBoundaries
desc = arcpy.Describe(frameworkBoundaries)
# Determine the extent of the frameworkBoundaries
extent = desc.Extent
# Cell size is one degree divided by lines per degree
linespd = 120 # for 30 arc second data
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
arcpy.AddMessage('Output grid has the following dimensions:')
print 'Output grid has the following dimensions:'
arcpy.AddMessage('Xmin:' + str(xmin))
print 'Xmin:' + str(xmin)
arcpy.AddMessage('YMin:'+ str(ymin))
print 'YMin:'+ str(ymin)
arcpy.AddMessage('XMax:'+ str(xmax))
print 'XMax:'+ str(xmax)
arcpy.AddMessage('YMax:'+ str(ymax))
print 'YMax:'+ str(ymax)
arcpy.AddMessage('Columns:'+ str(numCols))
print 'Columns:'+ str(numCols)
arcpy.AddMessage('Rows:   '+ str(numRows))
print 'Rows:   '+ str(numRows)
arcpy.AddMessage('Cell Size:   '+ str(cellSize))
print 'Cell Size:   '+ str(cellSize)
arcpy.AddMessage('Origin Coordinate:   '+ str(orgCoord))
print 'Origin Coordinate:   '+ str(orgCoord)
arcpy.AddMessage('Y Axis Coordinate:   '+ str(yaxisCoord))
print 'Y Axis Coordinate:   '+ str(yaxisCoord)
arcpy.AddMessage('Opposite Corner:   '+ str(oppCorner))
print 'Opposite Corner:   '+ str(oppCorner)
# Set coordinate system environment to WGS84
env.outputCoordinateSystem = arcpy.SpatialReference(4326)
# Calculate fishnet
fishnet = frameworkBoundaries + "_fishnet"
if arcpy.Exists(fishnet):
    arcpy.AddMessage(fishnet + " already exists")
    print fishnet + " already exists"
else:
    try:
        arcpy.CreateFishnet_management(fishnet,orgCoord,str(yaxisCoord),
                                       cellSizeWidth,cellSizeHeight,numRows,
                                       numCols, '#','NO_LABELS',
                                       frameworkBoundaries,'POLYGON')
        arcpy.AddMessage("Created " + fishnet)
        print "Created " + fishnet
    except:
        arcpy.GetMessages()
# Intersect fishnet with symBoundaries
intersectSym = fishnet + "_intersect"
inFeatures = [symBoundaries,fishnet]
if arcpy.Exists(intersectSym):
    arcpy.AddMessage(intersectSym + " already exists")
    print intersectSym + " already exists"
else:
    try:
        arcpy.Intersect_analysis(inFeatures, intersectSym)        
        arcpy.AddMessage("Created " + intersectSym)
        print "Created " + intersectSym
    except:
        arcpy.GetMessages()

# Create Intersect ID and Calculate it
INTRSCTID = "INTRSCTID"
try:
    if check_for_field(intersectSym,INTRSCTID)==0:
        arcpy.AddField_management(intersectSym,INTRSCTID,"LONG")
        arcpy.AddMessage("Added INTRSCTID")
        print "Added INTRSCTID"
    else:
        arcpy.AddMessage("INTRSCTID Already exists")
        print "INTRSCTID Already exists"
    arcpy.CalculateField_management(intersectSym,INTRSCTID,"!" + "OBJECTID" + "!","PYTHON")
    arcpy.AddMessage("Calculated INTRSCTID")
    print "Calculated INTRSCTID"
except:
    arcpy.AddMessage(arcpy.GetMessages())

# Convert intersectSym to points
intersectPoints = intersectSym + "_points"
if arcpy.Exists(intersectPoints):
    arcpy.AddMessage(intersectPoints + " already exists")
    print intersectPoints + " already exists"
else:
    try:
        arcpy.FeatureToPoint_management(intersectSym,intersectPoints,"INSIDE")
        arcpy.AddMessage("Created " + intersectPoints)
        print "Created " + intersectPoints
    except:
        arcpy.GetMessages()

# Spatial Join intersectPoints to clipBoundaries
spJoin = intersectPoints + "_spjoin"
if arcpy.Exists(spJoin):
    arcpy.AddMessage(spJoin + " already exists")
    print spJoin + " already exists"
else:
    try:
        arcpy.SpatialJoin_analysis(intersectPoints,clipBoundaries,spJoin,
                                   "#","KEEP_ALL","#","CLOSEST")
        arcpy.AddMessage("Created " + spJoin)
        print "Created " + spJoin
    except:
        arcpy.GetMessages()

# Join CLIPID from spJoin to intersectSym by INTRSCTID
try:
    # Create Attribute Indexes to make join faster
    arcpy.AddIndex_management(intersectSym,INTRSCTID,"INTRSCTID")
    arcpy.AddIndex_management(spJoin,INTRSCTID,"INTRSCTID")
    print "Added Indexes"
except:
    arcpy.GetMessages()
try:
    if check_for_field(intersectSym,CLIPID)==0:
        arcpy.JoinField_management(intersectSym,INTRSCTID,spJoin,INTRSCTID,CLIPID)
        arcpy.AddMessage("Joined CLIPID to: " + intersectSym)
        print "Joined CLIPID to: " + intersectSym
    else:
        arcpy.AddMessage("CLIPID Already exists in " +  intersectSym)
        print "CLIPID Already exists in " +  intersectSym
except:
    arcpy.GetMessages()

# Merge intersectSym with clipBoundaries
mergeBoundaries = inputBoundaries + "_merged"
if arcpy.Exists(mergeBoundaries):
    arcpy.AddMessage(mergeBoundaries + " already exists")
    print mergeBoundaries + " already exists"
else:
    try:
        arcpy.Merge_management([clipBoundaries,intersectSym] ,mergeBoundaries)
        arcpy.AddMessage("Created " + mergeBoundaries)
        print "Created " + mergeBoundaries
    except:
        arcpy.GetMessages()

# Dissolve mergeBoundaries by CLIPID
dissolveBoundaries = inputBoundaries + "_final"
if arcpy.Exists(dissolveBoundaries):
    arcpy.AddMessage(dissolveBoundaries + " already exists")
    print dissolveBoundaries + " already exists"
else:
    try:
        arcpy.Dissolve_management(mergeBoundaries,dissolveBoundaries,CLIPID)        
        arcpy.AddMessage("Created " + dissolveBoundaries)
        print "Created " + dissolveBoundaries
    except:
        arcpy.GetMessages()
        
# Join Attributes from clipBoundaries to dissolveBoundaries by CLIPID
# Check if the attributes have already been joined
fldList = arcpy.ListFields(dissolveBoundaries,"*")
# Create Attribute Indexes to make join faster
try:
    arcpy.AddIndex_management(dissolveBoundaries,CLIPID,"CLIPIDD")
    arcpy.AddIndex_management(clipBoundaries,CLIPID,"CLIPID")
    print "Added Indexes"
except:
    arcpy.GetMessages()
try:
    if len(fldList)<>5:
        arcpy.AddMessage("Attributes already exist in " +  dissolveBoundaries)
        print "Attributes already exist in " +  dissolveBoundaries
    else:
        arcpy.JoinField_management(dissolveBoundaries,CLIPID,clipBoundaries,CLIPID)
        arcpy.AddMessage("Joined attributes to: " + dissolveBoundaries)
        print "Joined attributes to: " + dissolveBoundaries
except:
    arcpy.GetMessages()

# Calculate FINALAREA
try:
    if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(dissolveBoundaries,"dissolveLyr1",'"' + "FINALAREA" + '"' + " IS NOT NULL"))[0])==0:
        arcpy.CalculateField_management(dissolveBoundaries,finalArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        print "Calculated " + finalArea
        arcpy.AddMessage("Calculated " + finalArea)
    else:
        print finalArea + " has already been calculated in " + os.path.basename(dissolveBoundaries)
        arcpy.AddMessage(finalArea + " has already been calculated in " + os.path.basename(dissolveBoundaries))
except:
    arcpy.GetMessages()

# Calculate CLIPAREADIFF
try:
    expression ="((!" + origArea + "!-!" + clipArea + "!)/!" + origArea + "!) * -100"
##    arcpy.CalculateField_management(inputBoundaries,clipAreaDiff,expression,'PYTHON')
    arcpy.CalculateField_management(dissolveBoundaries,clipAreaDiff,expression,'PYTHON')
    print "Calculated " + clipAreaDiff
    arcpy.AddMessage("Calculated " + clipAreaDiff)    
except:
    arcpy.GetMessages()

# Calculate FINALAREADIFF
try:
    expression ="((!" + origArea + "!-!" + finalArea + "!)/!" + origArea + "!) * -100"
##    arcpy.CalculateField_management(inputBoundaries,finalAreaDiff,expression,'PYTHON')
    arcpy.CalculateField_management(dissolveBoundaries,finalAreaDiff,expression,'PYTHON')
    print "Calculated " + finalAreaDiff
    arcpy.AddMessage("Calculated " + finalAreaDiff)    
except:
    arcpy.GetMessages()

# Clean up repeated fields
deleteList = arcpy.ListFields(dissolveBoundaries,"*_1")
if len(deleteList) == 0:
    arcpy.AddMessage("No fields to delete")
    print "No fields to delete"
else:
    for delFld in deleteList:
        try:
            arcpy.DeleteField_management(dissolveBoundaries, delFld.name)
            arcpy.AddMessage("Deleted " + delFld.name)
            print "Deleted " + delFld.name
        except:
            arcpy.GetMessages()

# Create feature layer which selects units that changed area substantially and exports them
try:
    errors = inputBoundaries + "_units_to_check"
    extraLayer = "extras"
    fl_selection = '"' + finalAreaDiff + '" < -5 OR "' + finalAreaDiff + '" > 5'
    arcpy.MakeFeatureLayer_management(dissolveBoundaries, extraLayer, fl_selection)
    print "Created " + extraLayer
    arcpy.AddMessage("Created " + extraLayer)
    arcpy.CopyFeatures_management(extraLayer,errors)
    print "Created " + errors
    arcpy.AddMessage("Created " + errors)
except:
    arcpy.GetMessages() 

arcpy.AddMessage("Algorithm is complete")
print "Algorithm is complete"
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
