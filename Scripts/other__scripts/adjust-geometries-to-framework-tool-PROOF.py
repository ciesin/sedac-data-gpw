# GPW Adjust Geometries to Framework
# Purpose: To Adjust Geometries to Match GADM International Boundary and Coastline
# Kytt MacManus
# September 7, 2012

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


# helper method to join fields
def joinFields(baseFeature,joinField,joinFeature,transferFields):
    # Make Feature Layers
    layer1 = baseFeature + "_lyr"
    layer2 = joinFeature + "_lyr"
    try:
        addTime = datetime.datetime.now()
        arcpy.MakeFeatureLayer_management(baseFeature,layer1)
        arcpy.MakeFeatureLayer_management(joinFeature,layer2)
        print "Made Feature Layers"
        arcpy.AddMessage("Made Feature Layers")
        print datetime.datetime.now() - addTime
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        arcpy.GetMessages()
    # Add Join
    try:
        addTime = datetime.datetime.now()
        arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_ALL")
        print "Added Join"
        arcpy.AddMessage("Added Join")
        print datetime.datetime.now() - addTime
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        print arcpy.GetMessages()
    # Transfer areaField
##    # List Fields
##    fields = arcpy.ListFields(layer1,"*")
##    for field in fields:
##        print field.name
    for transferField in transferFields:
        try:
            addTime = datetime.datetime.now()
            expression = '!' + os.path.basename(joinFeature) + "." + transferField + '!'
            arcpy.CalculateField_management(layer1,os.path.basename(baseFeature) + "." + transferField,expression,'PYTHON')
            print "Calculated " + transferField
            arcpy.AddMessage("Calculated " + transferField)
            print datetime.datetime.now() - addTime
            arcpy.AddMessage(datetime.datetime.now() - addTime)
        except:
            print arcpy.GetMessages()
    try:
        addTime = datetime.datetime.now()
        arcpy.RemoveJoin_management(layer1,os.path.basename(joinFeature))
        print "Removed temporary join"
        arcpy.AddMessage("Removed temporary join")
        print datetime.datetime.now() - addTime
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        print arcpy.GetMessages()  
    
# Define workspace
workspace = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\URY\Ingest\Boundary\boundary_adjustment.gdb'#arcpy.GetParameterAsText(0)
env.workspace = workspace
# Define Framework Boundaries
frameworkBoundaries = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\URY\Ingest\Boundary\boundary_adjustment.gdb\ury_gadm'# arcpy.GetParameterAsText(1)
#arcpy.GetParameterAsText(0)
#"D:\gpw4\ecu\ecu_boundaries.gdb\ecu_admin3_gadm2_mainland" ## ON ACADIA Because Add Field doesn't work over network
#r"\\DATASERVER0\gpw\GPW4\Working\Merge\ECU\staging\ecu_boundaries.gdb\ecu_admin3_gadm2_mainland"
# Define Input boundaries
inputBoundaries = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\URY\Ingest\Boundary\boundary_adjustment.gdb\ury_ine'# arcpy.GetParameterAsText(2)
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

        
### getCount of Clip Boundary Features
##clipCount = arcpy.GetCount_management(clipBoundaries)
##
### Compare counts for QAQC
##if str(inputCount) <> str(clipCount):
##    arcpy.AddMessage("There are " + str(inputCount) + " input features, but only " + str(clipCount) + " clip features...CHECK")
##    sys.exit("There are " + str(inputCount) + " input features, but only " + str(clipCount) + " clip features...CHECK")
##else:

    
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
        arcpy.GetMessages()

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

############

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

### join clipArea to inputFeatures
##try:
##    transferFields = [clipArea,finalArea]
##    joinTime = datetime.datetime.now()
##    joinArea(inputBoundaries,FRAMEWORKID,dissolveBoundaries,transferFields)
##    print "Joined " + str(transferFields) + " to " + inputBoundaries
##    arcpy.AddMessage("Joined " + str(transferFields) + " to " + inputBoundaries)
##    print datetime.datetime.now() - joinTime
##    arcpy.AddMessage(datetime.datetime.now() - joinTime)        
##except:
##    arcpy.GetMessages()

### Recode Nulls if there are any
##try:
##    if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(inputBoundaries,"inputlyr2",'"' + "CLIPAREA" + '"' + " IS NULL"))[0])==0:
##        pass
##    else:
##        nullLayer = "inputNullLyr1"
##        arcpy.MakeFeatureLayer_management(inputBoundaries,nullLayer,'"' + "CLIPAREA" + '"' + " IS NULL")
##        arcpy.CalculateField_management(nullLayer,clipArea,0,'PYTHON')
##        print "Recoded " + clipArea + " nulls"
##        arcpy.AddMessage("Recoded " + clipArea + " nulls")
##except:
##    arcpy.GetMessages()
##
### Recode Nulls if there are any
##try:
##    if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(inputBoundaries,"inputlyr4",'"' + "FINALAREA" + '"' + " IS NULL"))[0])==0:
##        pass
##    else:
##        nullLayer = "inputNullLyr2"
##        arcpy.MakeFeatureLayer_management(inputBoundaries,nullLayer,'"' + "FINALAREA" + '"' + " IS NULL")
##        arcpy.CalculateField_management(nullLayer,finalArea,0,'PYTHON')
##        print "Recoded " + finalArea + " nulls"
##        arcpy.AddMessage("Recoded " + finalArea + " nulls")
##except:
##    arcpy.GetMessages()

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

###USEFUL SNIPPETS FOR FUTURE USE

### Project Dataset to Mollweide
##mollweide = arcpy.SpatialReference(54009)
##proj1 = inputBoundaries + "_mollweide"
##if arcpy.Exists(proj1):
##    arcpy.AddMessage(proj1 + " already exists")
##    print proj1 + " already exists"
##else:
##    try:
##        arcpy.Project_management(inputBoundaries,proj1,mollweide)
##        print "Created " + proj1
##        arcpy.AddMessage("Created " + proj1)
##    except:
##        arcpy.GetMessages()
##        
### Calculate ORIGAREAKM 
##try:
##    if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(proj1,"proj1lyr",'"' + "ORIGAREAKM" + '"' + " IS NOT NULL"))[0])==0:
##        arcpy.CalculateField_management(proj1,origArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
##        print "Calculated " + origArea
##        arcpy.AddMessage("Calculated " + origArea)
##    else:
##        print origArea + " has already been calculated in " + proj1
##        arcpy.AddMessage(origArea + " has already been calculated in " + proj1)
##except:
##    arcpy.GetMessages()
##
### join ORIGAREAKM to inputFeatures
##try:
##    if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(inputBoundaries,"inputlyr1",'"' + "ORIGAREAKM" + '"' + " IS NOT NULL"))[0])==0:
##        joinTime = datetime.datetime.now()
##        joinArea(inputBoundaries,FRAMEWORKID,proj1,origArea)
##        print "Joined " + origArea + " to " + inputBoundaries
##        arcpy.AddMessage("Joined " + origArea + " to " + inputBoundaries)
##        print datetime.datetime.now() - joinTime
##        arcpy.AddMessage(datetime.datetime.now() - joinTime)
##    else:
##        print origArea + " has already been transfered to " + inputBoundaries
##        arcpy.AddMessage(origArea + " has already been transfered to " + inputBoundaries)        
##except:
##    arcpy.GetMessages()
