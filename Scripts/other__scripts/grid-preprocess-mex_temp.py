# grid-preprocess.py
# execute intermediate gridding steps to calculate fields for gridding
# Kytt MacManus
# February 2, 2013

# import libraries
import arcpy, os, sys
import datetime

# set counter
startTime = datetime.datetime.now()

# define inputs
##inFC = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\gmb.gdb\gmb_admin2_boundaries_2010'
inFC = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\mex.gdb\mex_admin2_boundaries_2010'
waterExist = "true"
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\mex.gdb'


# define workspace environment
arcpy.env.workspace = workspace

# define gridding resolution
# Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
# 1 degree divided into 120 parts is 30 seconds
linespd = 120
##linespd = arcpy.GetParameterAsText(1)

# parse inFC to determine rootName
rootName = os.path.basename(inFC)[:3]

# define input fishnet
inFish = rootName + "_fishnet"

# check to see that fishnet exists, if it doesn't kill the script
if not arcpy.Exists(inFish):
    sys.exit("The input fishnet does not exist, check the geodatabase")

# define estimatesTable
estimatesTable = rootName + "_estimates"

# first check that the UBID field exists in both the estimates and boundaries, if not exit
if not len(arcpy.ListFields(inFC,"UBID"))==1:
    sys.exit("The boundaries are missing UBID")
elif not len(arcpy.ListFields(estimatesTable,"UBID"))==1:
    sys.exit("The census data is missing UBID")         
else:
    pass

# check to see that estimates exists, if it doesn't kill the script
if not arcpy.Exists(estimatesTable):
    sys.exit("The input census estimates do not exist, check the geodatabase")

# define spatial reference
prjFile = r'\\Dataserver0\gpw\GPW4\Gridding\country\custom_projections' + os.path.sep + rootName + "_mollweide.prj"
# check to see that estimates exists, if it doesn't kill the script
if not arcpy.Exists(prjFile):
    sys.exit("The input prj file does not exist, check the network")
else:
    spatialRef = open(prjFile,"r").read()

#######################################################################################

# make a copy of inFC
inFCG = inFC + "_gridding"
##try:
##    arcpy.Copy_management(inFC,inFCG)
##except:
##    arcpy.GetMessages()
    
# add a tmpid field and calculate it equal to the OBJECTID
try:
    tmpid = "TEMPID"
##    arcpy.AddField_management(inFCG,tmpid,'LONG','12')
##    arcpy.CalculateField_management(inFCG,tmpid,'!OBJECTID!','PYTHON')
    arcpy.AddMessage("calculated " + tmpid)
except:
    arcpy.GetMessages()    

# project inFCG to mollweide
try:
    projectFC = inFC + "_mollweide"
##    arcpy.Project_management(inFCG, projectFC, spatialRef)
    arcpy.AddMessage("created " + projectFC)
except:
    arcpy.GetMessages()

# add ADMINAREAKM and calculate
try:
    adminArea = "ADMINAREAKM"
##    arcpy.AddField_management(projectFC,adminArea,'DOUBLE')
##    arcpy.CalculateField_management(projectFC,adminArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
    arcpy.AddMessage("calculated " + adminArea)
except:
    arcpy.GetMessages()

# join ADMINAREAKM to inFCG
try:
    joinTime = datetime.datetime.now()
##    arcpy.JoinField_management(inFCG,tmpid,projectFC,tmpid,adminArea)
    arcpy.AddMessage("joined " + adminArea + " to " + inFCG)
    arcpy.AddMessage(datetime.datetime.now() - joinTime)
except:
    arcpy.GetMessages()
   
if waterExist == "true":
    # define input waterMask
    waterMask = rootName + "_water_mask"
    # check to see that waterMask exists, if it doesn't kill the script
    if not arcpy.Exists(waterMask):
        sys.exit("The input water mask does not exist, but the parameter states that it should. Verify that it should or should not")
    # clip inFC to waterMask
    waterFC = rootName + "_water_areas"
    try:
##        arcpy.Clip_analysis(inFCG,waterMask,waterFC)
        arcpy.AddMessage("Created " + waterFC)
    except:
        arcpy.GetMessages
        
    # project waterFC to mollweide
    try:
        waterProjectFC = waterFC + "_mollweide"
##        arcpy.Project_management(waterFC, waterProjectFC, spatialRef)
        arcpy.AddMessage("created " + waterProjectFC)
    except:
        arcpy.GetMessages()

    # add ADMINWATERAREAKM and calculate
    try:
        adminWaterArea = "ADMINWATERAREAKM"
##        arcpy.AddField_management(waterProjectFC,adminWaterArea,'DOUBLE')
##        arcpy.CalculateField_management(waterProjectFC,adminWaterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        arcpy.AddMessage("calculated " + adminWaterArea)
    except:
        arcpy.GetMessages()


    # join ADMINWATERAREAKM to inFCG
    try:
        joinTime = datetime.datetime.now()
##        arcpy.JoinField_management(inFCG,tmpid,waterProjectFC,tmpid,adminWaterArea)
        arcpy.AddMessage("joined " + adminWaterArea + " to " + inFCG)
        arcpy.AddMessage(datetime.datetime.now() - joinTime)
    except:
        arcpy.GetMessages()

    # Need to convert Nulls to Zeros
    try:
        adminWaterLYR = "adminwaterlyr"
        arcpy.MakeFeatureLayer_management(inFCG,adminWaterLYR,adminWaterArea + " IS NULL")
##        arcpy.CalculateField_management(adminWaterLYR,adminWaterArea,0, "PYTHON")
        arcpy.AddMessage("Recoded Nulls")
    except:
        arcpy.GetMessages()
else:
    # define input waterMask
    waterMask = rootName + "_water_mask"
    # check to see that waterMask exists, if it doesn't kill the script
    if arcpy.Exists(waterMask):
        sys.exit("The input water mask exists, but the parameter states that it shouldn't. Verify that it should or should not")
    # add ADMINWATERAREAKM and calculate
    try:
        adminWaterArea = "ADMINWATERAREAKM"
##        arcpy.AddField_management(inFCG,adminWaterArea,'DOUBLE')
##        arcpy.CalculateField_management(inFCG,adminWaterArea,0,'PYTHON')
        arcpy.AddMessage("calculated " + adminWaterArea)
    except:
        arcpy.GetMessages()

## add ADMINAREAKMMASKED to inFCG and calculate
try:
    maskedArea = "ADMINAREAKMMASKED"
##    arcpy.AddField_management(inFCG,maskedArea,'DOUBLE')
##    arcpy.CalculateField_management(inFCG,maskedArea,'!' + adminArea + '! - !' + adminWaterArea + "!",'PYTHON')
    arcpy.AddMessage("calculated " + maskedArea)
except:
    arcpy.GetMessages()

# join fields from estimates table to inFCG
# must first create a list of fields and append their names to fieldList
fieldList = []
flds = arcpy.ListFields(estimatesTable,"ATOT*")
for fld in flds:
    fieldList.append(fld.name)
flds2 = arcpy.ListFields(estimatesTable,"*E_ATOT*")
for fld2 in flds2:
    fieldList.append(fld2.name)
# join estimates fields to inFCG
try:
    joinTime = datetime.datetime.now()
##    arcpy.JoinField_management(inFCG,"UBID",estimatesTable,"UBID",fieldList)
    arcpy.AddMessage("joined estimates fields to " + inFCG)
    arcpy.AddMessage(datetime.datetime.now() - joinTime)
except:
    arcpy.GetMessages()

### This section is adapted from calcdensities.py as written
### by Greg Yetman circa 2010
# iterate estimates fields and calculate densities
# Create a table view to avoid division by zero
tblSel = 'tblSel'
whereCls = adminArea + ' > 0'
tblSel = arcpy.MakeTableView_management(inFCG,tblSel,whereCls)
for field in fieldList:
    # define density field
    dsField = field + "_DS"
    # define masked density field
    maskedDSField = field + "_DSM"
##    # add density field and masked density field
##    try:
##        arcpy.AddField_management(inFCG,dsField,'DOUBLE')
##        arcpy.AddField_management(inFCG,maskedDSField,'DOUBLE')
##    except:
##        arcpy.GetMessages()    
    # do the division
    exp = '!' + field + '! / !' + adminArea + '!'
    exp2 = '!' + field + '! / !' + maskedArea + '!'
##    try:
####        arcpy.CalculateField_management(tblSel,dsField,exp,'PYTHON')
####        print "Calculated " + dsField
##        arcpy.CalculateField_management(tblSel,maskedDSField,exp2,'PYTHON')
####        print "Calculated " + maskedDSField
##    except:
##        arcpy.GetMessages()

# clip the fishnet to the input fc extent        
clipnet = inFC + "_fishnet_clipped"
try:
##    arcpy.Clip_analysis(inFish,inFCG,clipnet)
    arcpy.AddMessage('Clipped fishnet to ' + inFCG)
except:
    arcpy.GetMessages()
    
# intersect fishnet and inFCG
clipnetInt = clipnet + "_intersect"
inFeatures = [inFCG,clipnet]
try:
##    arcpy.Intersect_analysis(inFeatures, clipnetInt)
    arcpy.AddMessage('Intersected clipped fishnet and input features.')
except:
    arcpy.GetMessages()

# add and calculate another unique id field called INTRSCTID
INTRSCTID = "INTRSCTID"
try:
##    arcpy.AddField_management(clipnetInt,INTRSCTID,'LONG')
##    arcpy.CalculateField_management(clipnetInt,INTRSCTID,'!OBJECTID!','PYTHON')
    indexTest1 = arcpy.ListIndexes(clipnetInt,INTRSCTID + "_index")
    if len(indexTest1) == 1:
        pass
    else:
        arcpy.AddIndex_management(clipnetInt,INTRSCTID,INTRSCTID + "_index","UNIQUE")
    arcpy.AddMessage("Calculated " + INTRSCTID)
except:
    arcpy.GetMessages()
    
# project clipnetInt to mollweideCustom
try:        
    clipnetIntProjected = clipnetInt + '_projected'
##    arcpy.Project_management(clipnetInt,clipnetIntProjected,spatialRef)
    indexTest2 = arcpy.ListIndexes(clipnetIntProjected,INTRSCTID + "_index")
    if len(indexTest2) == 1:
        pass
    else:
        arcpy.AddIndex_management(clipnetIntProjected,INTRSCTID,INTRSCTID + "_index","UNIQUE")
    arcpy.AddMessage("Projected " + clipnetInt)
except:
    arcpy.GetMessages()

# add an area field to clipnetIntProjected
featureArea = "AREAKM"
try:
##    arcpy.AddField_management(clipnetIntProjected,featureArea,'DOUBLE')
##    arcpy.CalculateField_management(clipnetIntProjected,featureArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
    arcpy.AddMessage("Calculated " + featureArea)
except:
    arcpy.GetMessages()

# join featureArea to clipnetInt
try:
    joinTime = datetime.datetime.now()
##    arcpy.JoinField_management(clipnetInt,INTRSCTID,clipnetIntProjected,INTRSCTID,featureArea)
    arcpy.AddMessage("Joined " + featureArea + " to " + clipnetInt)
    arcpy.AddMessage(datetime.datetime.now() - joinTime)
except:
    arcpy.GetMessages()

if waterExist =="true":
    # clip clipnetInt to the waterMask extent        
    clipwatInt = inFC + "_water_mask_clipped_intersect"
    try:
##        arcpy.Clip_analysis(clipnetInt,waterMask,clipwatInt)
        arcpy.AddMessage('Clipped fishnet to ' + waterMask)
    except:
        arcpy.GetMessages()
        
    # project clipwatInt to mollweideCustom
    try:        
        clipwatIntProjected = clipwatInt + '_projected'
##        arcpy.Project_management(clipwatInt,clipwatIntProjected,spatialRef)    
        arcpy.AddMessage("Projected " + clipwatInt)
    except:
        arcpy.GetMessages()

    # add an area field to clipnetIntProjected
    waterArea = "WATERAREAKM"
    try:
##        arcpy.AddField_management(clipwatIntProjected,waterArea,'DOUBLE')
##        arcpy.CalculateField_management(clipwatIntProjected,waterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        arcpy.AddMessage("Calculated " + waterArea)
    except:
        arcpy.GetMessages()

    # join waterArea to clipnetInt
    try:
        joinTime = datetime.datetime.now()
##        arcpy.JoinField_management(clipnetInt,INTRSCTID,clipwatIntProjected,INTRSCTID,waterArea)
        arcpy.AddMessage("Joined " + waterArea + " to " + clipnetInt)
        arcpy.AddMessage(datetime.datetime.now() - joinTime)
    except:
        arcpy.GetMessages()

    # Need to convert Nulls to Zeros
    try:
        waterLYR = "fishnetwaterlyr"
        arcpy.MakeFeatureLayer_management(clipnetInt,waterLYR,waterArea + " IS NULL")
##        arcpy.CalculateField_management(waterLYR,waterArea,0, "PYTHON")
        arcpy.AddMessage("Recoded Nulls")
    except:
        arcpy.GetMessages()
else:
    # add an area field to clipnetIntProjected
    waterArea = "WATERAREAKM"
    try:
##        arcpy.AddField_management(clipnetInt,waterArea,'DOUBLE')
##        arcpy.CalculateField_management(clipnetInt,waterArea,0,'PYTHON')
        arcpy.AddMessage("Calculated " + waterArea)
    except:
        arcpy.GetMessages()
# add and calculate the areakmmasked field
try:
    maskedFeatureArea = "AREAKMMASKED"
##    arcpy.AddField_management(clipnetInt,maskedFeatureArea,'DOUBLE')
##    arcpy.CalculateField_management(clipnetInt,maskedFeatureArea,'!' + featureArea + '! - !' + waterArea + "!",'PYTHON')
    arcpy.AddMessage("calculated " + maskedFeatureArea)
except:
    arcpy.GetMessages()


# Create in memory version of clipnetInt
clipnetIntMem = "in_memory" + os.sep + os.path.basename(clipnetInt)
try:
    joinTime = datetime.datetime.now()
##    arcpy.CopyFeatures_management(clipnetInt,clipnetIntMem)
    print "Created " + clipnetIntMem
    print datetime.datetime.now() - joinTime
except:
    print arcpy.GetMessages()

# define cntFields list.  this is a list of fields to be aggregated by adminID
cntFields = [[featureArea,'SUM'],[waterArea,'SUM'],[maskedFeatureArea,'SUM']]
joinCNTFields = ["SUM_" + featureArea, "SUM_" + waterArea, "SUM_" + maskedFeatureArea]

# iterate the fields list to calculate counts
for field in fieldList:
    # define density field
    dsField = field + "_DS"
    # define masked density field
    maskedDSField = field + "_DSM"
    # define count field
    cntField = field + "_CNT"
    # define masked count field
    maskedCNTField = field + "_CNTM"
    # append to cntFields
    cntFields.append([cntField,'SUM'])
    cntFields.append([maskedCNTField,'SUM'])
    joinCNTFields.append("SUM_" + cntField)
    joinCNTFields.append("SUM_" + maskedCNTField)    
   
##    # add count field and calculate
##    try:
##        joinTime = datetime.datetime.now()
##        # check if field exists
##        fldCheck = arcpy.ListFields(clipnetIntMem,cntField)
##        if len(fldCheck) == 1:
##            pass
##        else:
##            arcpy.AddField_management(clipnetIntMem,cntField,'Double')
##            arcpy.AddField_management(clipnetIntMem,maskedCNTField,'Double')
##            arcpy.CalculateField_management(clipnetIntMem,cntField,"!" + featureArea + "! * !"
##                                            + dsField + "!","PYTHON")
##            arcpy.CalculateField_management(clipnetIntMem,maskedCNTField,"!" + maskedFeatureArea + "! * !"
##                                            + maskedDSField + "!","PYTHON")
##        arcpy.AddMessage("Calculated Population in " + cntField + " and " + maskedCNTField)
##        print "Calculated Population in " + cntField + " and " + maskedCNTField
##        print datetime.datetime.now() - joinTime
##    except:
##        arcpy.GetMessages()

# Create disk version of clipnetIntMem
clipnetInt2 = clipnetInt + "_v2"
try:
    joinTime = datetime.datetime.now()
##    arcpy.CopyFeatures_management(clipnetIntMem,clipnetInt2)
    print "Created " + clipnetInt2
    print datetime.datetime.now() - joinTime
    clipnetInt = clipnetInt2
except:
    print arcpy.GetMessages()
        
# Sum proportional allocation count fields 
sumTbl = inFC + "_aggregated_estimates"
pixelID = "PIXELID"
try:
    joinTime = datetime.datetime.now()
    arcpy.Statistics_analysis(clipnetInt,sumTbl,cntFields,pixelID)
    arcpy.AddIndex_management(sumTbl,pixelID,pixelID + "_index","UNIQUE")    
    print "Calculated Statistics"
    print datetime.datetime.now() - joinTime
except:
    arcpy.GetMessages()

# join results to the original fishnet
# first check that the fishnet has an index, if not build one
if not len(arcpy.ListIndexes(inFish,"PIXELID_index"))==1:
    arcpy.AddIndex_management(inFish,pixelID,pixelID + "_index","UNIQUE")
else:
    pass
# next perform the join
try:
    joinTime = datetime.datetime.now()
    arcpy.JoinField_management(inFish,"PIXELID",sumTbl,"PIXELID",joinCNTFields)
    print "Joined Statistic Fields to " + inFish
    print datetime.datetime.now() - joinTime
except:
    arcpy.GetMessages()

arcpy.AddMessage(datetime.datetime.now() - startTime) 
