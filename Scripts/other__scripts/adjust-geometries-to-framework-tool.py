# GPW Adjust Geometries to Framework
# Purpose: To Adjust Geometries to Match GADM International Boundary and Coastline
# Kytt MacManus
# September 7, 2012

# Import Python Libraries
import arcpy, os, sys
from arcpy import env

# Set Overwrite Output Environment
env.overwriteOutput = 1

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
workspace = arcpy.GetParameterAsText(0)
env.workspace = workspace
# Define Framework Boundaries
frameworkBoundaries = arcpy.GetParameterAsText(1)
#arcpy.GetParameterAsText(0)
#"D:\gpw4\ecu\ecu_boundaries.gdb\ecu_admin3_gadm2_mainland" ## ON ACADIA Because Add Field doesn't work over network
#r"\\DATASERVER0\gpw\GPW4\Working\Merge\ECU\staging\ecu_boundaries.gdb\ecu_admin3_gadm2_mainland"
# Define Input boundaries
inputBoundaries = arcpy.GetParameterAsText(2)
#arcpy.GetParameterAsText(1)
#"D:\gpw4\ecu\ecu_boundaries.gdb\ecu_admin3_inec_mainland"
#r"\\DATASERVER0\gpw\GPW4\Working\Merge\ECU\staging\ecu_boundaries.gdb\ecu_admin3_inec_mainland"

# Create Framework ID and Calculate it
FRAMEWORKID = "FRAMEID"
try:
    if check_for_field(frameworkBoundaries,FRAMEWORKID)==0:
        arcpy.AddField_management(frameworkBoundaries,FRAMEWORKID,"LONG")
        arcpy.AddMessage("Added FRAMEWORKID")
    else:
        arcpy.AddMessage("FRAMEWORKID Already exists")
    arcpy.CalculateField_management(frameworkBoundaries,FRAMEWORKID,"[" + "OBJECTID" +"]")
    arcpy.AddMessage("Calculated FRAMEWORKID")
except:
    arcpy.AddMessage(arcpy.GetMessages())
                    
# getCount of Input Boundary Features
inputCount = arcpy.GetCount_management(inputBoundaries)

# Clip Input Boundaries to Framework Boundaries
clipBoundaries = inputBoundaries + "_clip"
if arcpy.Exists(clipBoundaries):
    arcpy.AddMessage(clipBoundaries + " already exists")
else:
    try:
        arcpy.Clip_analysis(inputBoundaries,frameworkBoundaries,clipBoundaries)
        arcpy.AddMessage("Created " + clipBoundaries)
    except:
        arcpy.GetMessages()
        
# getCount of Clip Boundary Features
clipCount = arcpy.GetCount_management(clipBoundaries)

# Compare counts for QAQC
if str(inputCount) <> str(clipCount):
    arcpy.AddMessage("There are " + str(inputCount) + " input features, but only " + str(clipCount) + " clip features...CHECK")
##    sys.exit("There are " + str(inputCount) + " input features, but only " + str(clipCount) + " clip features...CHECK")
else:        
    # Find symmetrical difference of clipBoundaries and frameworkBoundaries
    symBoundaries = clipBoundaries + "_symdiff"
    if arcpy.Exists(symBoundaries):
        arcpy.AddMessage(symBoundaries + " already exists")
    else:
        try:
            arcpy.SymDiff_analysis(clipBoundaries,frameworkBoundaries,symBoundaries,
                                   "ALL")
            arcpy.AddMessage("Created " + symBoundaries)
        except:
            arcpy.GetMessages()

    # Create Clip ID and Calculate it
    CLIPID = "CLIPID"
    try:
        if check_for_field(clipBoundaries,CLIPID)==0:
            arcpy.AddField_management(clipBoundaries,CLIPID,"LONG")
            arcpy.AddMessage("Added CLIPID")
        else:
            arcpy.AddMessage("CLIPID Already exists")
        arcpy.CalculateField_management(clipBoundaries,CLIPID,"[" + "OBJECTID" +"]")
        arcpy.AddMessage("Calculated CLIPID")
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
    arcpy.AddMessage('Xmin:' + str(xmin))
    arcpy.AddMessage('YMin:'+ str(ymin))
    arcpy.AddMessage('XMax:'+ str(xmax))
    arcpy.AddMessage('YMax:'+ str(ymax))
    arcpy.AddMessage('Columns:'+ str(numCols))
    arcpy.AddMessage('Rows:   '+ str(numRows))
    arcpy.AddMessage('Cell Size:   '+ str(cellSize))
    arcpy.AddMessage('Origin Coordinate:   '+ str(orgCoord))
    arcpy.AddMessage('Y Axis Coordinate:   '+ str(yaxisCoord))
    arcpy.AddMessage('Opposite Corner:   '+ str(oppCorner))
    # Set coordinate system environment to WGS84
    env.outputCoordinateSystem = arcpy.SpatialReference(4326)
    # Calculate fishnet
    fishnet = frameworkBoundaries + "_fishnet"
    if arcpy.Exists(fishnet):
        arcpy.AddMessage(fishnet + " already exists")
    else:
        try:
            arcpy.CreateFishnet_management(fishnet,orgCoord,str(yaxisCoord),
                                           cellSizeWidth,cellSizeHeight,numRows,
                                           numCols, '#','NO_LABELS',
                                           frameworkBoundaries,'POLYGON')
            arcpy.AddMessage("Created " + fishnet)
        except:
            arcpy.GetMessages()
    # Intersect fishnet with symBoundaries
    intersectSym = symBoundaries + "_intersect"
    inFeatures = [symBoundaries,fishnet]
    if arcpy.Exists(intersectSym):
        arcpy.AddMessage(intersectSym + " already exists")
    else:
        try:
            arcpy.Intersect_analysis(inFeatures, intersectSym)        
            arcpy.AddMessage("Created " + intersectSym)
        except:
            arcpy.GetMessages()

    # Create Intersect ID and Calculate it
    INTRSCTID = "INTRSCTID"
    try:
        if check_for_field(intersectSym,INTRSCTID)==0:
            arcpy.AddField_management(intersectSym,INTRSCTID,"LONG")
            arcpy.AddMessage("Added INTRSCTID")
        else:
            arcpy.AddMessage("INTRSCTID Already exists")
        
        arcpy.CalculateField_management(intersectSym,INTRSCTID,"[" + "OBJECTID" + "]")
        arcpy.AddMessage("Calculated INTRSCTID")
    except:
        arcpy.AddMessage(arcpy.GetMessages())

    # Convert intersectSym to points
    intersectPoints = intersectSym + "_points"
    if arcpy.Exists(intersectPoints):
        arcpy.AddMessage(intersectPoints + " already exists")
    else:
        try:
            arcpy.FeatureToPoint_management(intersectSym,intersectPoints,"INSIDE")
            arcpy.AddMessage("Created " + intersectPoints)
        except:
            arcpy.GetMessages()

    # Spatial Join intersectPoints to clipBoundaries
    spJoin = intersectPoints + "_spjoin"
    if arcpy.Exists(spJoin):
        arcpy.AddMessage(spJoin + " already exists")    
    else:
        try:
            arcpy.SpatialJoin_analysis(intersectPoints,clipBoundaries,spJoin,
                                       "#","KEEP_ALL","#","CLOSEST")
            arcpy.AddMessage("Created " + spJoin)        
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
        else:
            arcpy.AddMessage("CLIPID Already exists in " +  intersectSym)
    except:
        arcpy.GetMessages()

    # Merge intersectSym with clipBoundaries
    mergeBoundaries = inputBoundaries + "_merged"
    if arcpy.Exists(mergeBoundaries):
        arcpy.AddMessage(mergeBoundaries + " already exists")    
    else:
        try:
            arcpy.Merge_management([clipBoundaries,intersectSym] ,mergeBoundaries)
            arcpy.AddMessage("Created " + mergeBoundaries)
        except:
            arcpy.GetMessages()

    # Dissolve mergeBoundaries by CLIPID
    dissolveBoundaries = inputBoundaries + "_adjusted"
    if arcpy.Exists(dissolveBoundaries):
        arcpy.AddMessage(dissolveBoundaries + " already exists")    
    else:
        try:
            arcpy.Dissolve_management(mergeBoundaries,dissolveBoundaries,CLIPID)        
            arcpy.AddMessage("Created " + dissolveBoundaries)
        except:
            arcpy.GetMessages()
            
    # Join Attributes from clipBoundaries to dissolveBoundaries by CLIPID
    # Check if the attributes have already been joined
    fldList = arcpy.ListFields(dissolveBoundaries,"*")
    # Create Attribute Indexes to make join faster
    try:
        arcpy.AddIndex_management(dissolveBoundaries,CLIPID,"CLIPID")
        arcpy.AddIndex_management(clipBoundaries,CLIPID,"CLIPID")
        print "Added Indexes"
    except:
        arcpy.GetMessages()
    try:
        if len(fldList)<>5:
            arcpy.AddMessage("Attributes already exist in " +  dissolveBoundaries)       
        else:
            arcpy.JoinField_management(dissolveBoundaries,CLIPID,clipBoundaries,CLIPID)
            arcpy.AddMessage("Joined attributes to: " + dissolveBoundaries)       
    except:
        arcpy.GetMessages()

    # Clean up repeated fields
    deleteList = arcpy.ListFields(dissolveBoundaries,"*_1")
    if len(deleteList) == 0:
        arcpy.AddMessage("Algorithm is complete")
    else:
        for delFld in deleteList:
            try:
                arcpy.DeleteField_management(dissolveBoundaries, delFld.name)
                arcpy.AddMessage( "Deleted " + delFld.name)
            except:
                arcpy.GetMessages()
    arcpy.AddMessage("Algorithm is complete")


