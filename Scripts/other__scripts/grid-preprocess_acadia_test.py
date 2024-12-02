# grid-preprocess.py
# execute intermediate gridding steps to calculate fields for gridding
# Kytt MacManus
# February 2, 2013

# import libraries
import arcpy, os, sys
import datetime

# set counter
startTime = datetime.datetime.now()

# define input feature class
inFC = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\btn_acadia.gdb\btn_boundaries_2010'
##inFC = arcpy.GetParameterAsText(0)

# define gridding resolution
# Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
# 1 degree divided into 120 parts is 30 seconds
linespd = 120
##linespd = arcpy.GetParameterAsText(1)

# parse inFC to determine rootName
rootName = os.path.basename(inFC)[:3]

# define input waterMask
waterMask = inFC.replace("boundaries_2010","water_mask")

# check to see that waterMask exists, if it doesn't kill the script
if not arcpy.Exists(waterMask):
    sys.exit("The input water mask does not exist, check the geodatabase")

# define input fishnet
inFish = inFC.replace("boundaries_2010","fishnet")

# check to see that fishnet exists, if it doesn't kill the script
if not arcpy.Exists(inFish):
    sys.exit("The input fishnet does not exist, check the geodatabase")

# define estimatesTable
estimatesTable = inFC.replace("boundaries_2010","estimates")

# check to see that estimates exists, if it doesn't kill the script
if not arcpy.Exists(estimatesTable):
    sys.exit("The input census estimates do not exist, check the geodatabase")

# define spatial reference
prjFile = r'\\Dataserver0\gpw\GPW4\Gridding\country\custom_projections' + os.path.sep + rootName + "_mollweide.prj"
# check to see that estimates exists, if it doesn't kill the script
if not arcpy.Exists(prjFile):
    sys.exit("The input census estimates do not exist, check the geodatabase")
else:
    spatialRef = open(prjFile,"r").read()

#####################################################################################

# make a copy of inFC
inFCG = inFC + "_gridding"
try:
    arcpy.Copy_management(inFC,inFCG)
except:
    arcpy.GetMessages()
    
# add a tmpid field and calculate it equal to the OBJECTID
try:
    tmpid = "TEMPID"
    arcpy.AddField_management(inFCG,tmpid,'LONG','12')
    arcpy.CalculateField_management(inFCG,tmpid,'!OBJECTID!','PYTHON')
    print "calculated " + tmpid
except:
    arcpy.GetMessages()    

# project inFCG to mollweide
try:
    projectFC = inFC + "_mollweide"
    arcpy.Project_management(inFCG, projectFC, spatialRef)
    print "created " + projectFC
except:
    arcpy.GetMessages()

# add ADMINAREAKM and calculate
try:
    adminArea = "ADMINAREAKM"
    arcpy.AddField_management(projectFC,adminArea,'DOUBLE')
    arcpy.CalculateField_management(projectFC,adminArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
    print "calculated " + adminArea
except:
    arcpy.GetMessages()

# join ADMINAREAKM to inFCG
try:
    joinTime = datetime.datetime.now()
    arcpy.JoinField_management(inFCG,tmpid,projectFC,tmpid,adminArea)
    print "joined " + adminArea + " to " + inFCG
    print datetime.datetime.now() - joinTime
except:
    arcpy.GetMessages()

# clip inFC to waterMask
waterFC = inFC + "_water_areas"
try:
    arcpy.Clip_analysis(inFCG,waterMask,waterFC)
    print "Created " + waterFC
except:
    arcpy.GetMessages
    
# project waterFC to mollweide
try:
    waterProjectFC = waterFC + "_mollweide"
    arcpy.Project_management(waterFC, waterProjectFC, spatialRef)
    print "created " + waterProjectFC
except:
    arcpy.GetMessages()

# add ADMINWATERAREAKM and calculate
try:
    adminWaterArea = "ADMINWATERAREAKM"
    arcpy.AddField_management(waterProjectFC,adminWaterArea,'DOUBLE')
    arcpy.CalculateField_management(waterProjectFC,adminWaterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
    print "calculated " + adminWaterArea
except:
    arcpy.GetMessages()

# join ADMINWATERAREAKM to inFCG
try:
    joinTime = datetime.datetime.now()
    arcpy.JoinField_management(inFCG,tmpid,waterProjectFC,tmpid,adminWaterArea)
    print "joined " + adminWaterArea + " to " + inFCG
    print datetime.datetime.now() - joinTime
except:
    arcpy.GetMessages()

# add ADMINAREAKMMASKED to inFCG and calculate
try:
    maskedArea = "ADMINAREAKMMASKED"
    arcpy.AddField_management(inFCG,maskedArea,'DOUBLE')
    arcpy.CalculateField_management(inFCG,maskedArea,'!' + adminArea + '! - !' + adminWaterArea + "!",'PYTHON')
    print "calculated " + maskedArea
except:
    arcpy.GetMessages()

# join fields from estimates table to inFCG
# must first create a list of fields and append their names to fieldList
fieldList = []
flds = arcpy.ListFields(estimatesTable,"*E_A*")
for fld in flds:
    fieldList.append(fld.name)
# join estimates fields to inFCG
try:
    joinTime = datetime.datetime.now()
    arcpy.JoinField_management(inFCG,"UID_BOUNDARY",estimatesTable,"UID_BOUNDARY",fieldList)
    print "joined estimates fields to " + inFCG
    print datetime.datetime.now() - joinTime
except:
    arcpy.GetMessages()

### This section is adapted form calcdensities.py as written
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
    # add density field and masked density field
    try:
        arcpy.AddField_management(inFCG,dsField,'DOUBLE')
        arcpy.AddField_management(inFCG,maskedDSField,'DOUBLE')
    except:
        arcpy.GetMessages()    
    # do the division
    exp = '!' + field + '! / !' + adminArea + '!'
    exp2 = '!' + field + '! / !' + maskedArea + '!'
    try:
        arcpy.CalculateField_management(tblSel,dsField,exp,'PYTHON')
##        print "Calculated " + dsField
        arcpy.CalculateField_management(tblSel,maskedDSField,exp2,'PYTHON')
##        print "Calculated " + maskedDSField
    except:
        arcpy.GetMessages()

# clip the fishnet to the input fc extent        
clipnet = inFC + "_fishnet_clipped"
try:
    arcpy.Clip_analysis(inFish,inFCG,clipnet)
    print 'Clipped fishnet to ' + inFCG
except:
    arcpy.GetMessages()
    
# intersect fishnet and inFCG
clipnetInt = clipnet + "_intersect"
inFeatures = [inFCG,clipnet]
try:
    arcpy.Intersect_analysis(inFeatures, clipnetInt)
    print 'Intersected clipped fishnet and input features.'
except:
    arcpy.GetMessages()

# add and calculate another unique id field called INTRSCTID
INTRSCTID = "INTRSCTID"
try:
    arcpy.AddField_management(clipnetInt,INTRSCTID,'LONG')
    arcpy.CalculateField_management(clipnetInt,INTRSCTID,'!OBJECTID!','PYTHON')
    arcpy.AddIndex_management(clipnetInt,INTRSCTID,INTRSCTID + "_index","UNIQUE")
    print "Calculated " + INTRSCTID
except:
    arcpy.GetMessages()
    
# project clipnetInt to mollweideCustom
try:        
    clipnetIntProjected = clipnetInt + '_projected'
    arcpy.Project_management(clipnetInt,clipnetIntProjected,spatialRef)
    arcpy.AddIndex_management(clipnetIntProjected,INTRSCTID,INTRSCTID + "_index","UNIQUE")
    print "Projected " + clipnetInt
except:
    arcpy.GetMessages()

# add an area field to clipnetIntProjected
featureArea = "AREAKM"
try:
    arcpy.AddField_management(clipnetIntProjected,featureArea,'DOUBLE')
    arcpy.CalculateField_management(clipnetIntProjected,featureArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
    print "Calculated " + featureArea
except:
    arcpy.GetMessages()

# join featureArea to clipnetInt
try:
    joinTime = datetime.datetime.now()
    arcpy.JoinField_management(clipnetInt,INTRSCTID,clipnetIntProjected,INTRSCTID,featureArea)
    print "Joined " + featureArea + " to " + clipnetInt
    print datetime.datetime.now() - joinTime
except:
    arcpy.GetMessages()

# clip clipnetInt to the waterMask extent        
clipwatInt = inFC + "_water_mask_clipped_intersect"
try:
    arcpy.Clip_analysis(clipnetInt,waterMask,clipwatInt)
    print 'Clipped fishnet to ' + waterMask
except:
    arcpy.GetMessages()
    
# project clipwatInt to mollweideCustom
try:        
    clipwatIntProjected = clipwatInt + '_projected'
    arcpy.Project_management(clipwatInt,clipwatIntProjected,spatialRef)    
    print "Projected " + clipwatInt
except:
    arcpy.GetMessages()

# add an area field to clipnetIntProjected
waterArea = "WATERAREAKM"
try:
    arcpy.AddField_management(clipwatIntProjected,waterArea,'DOUBLE')
    arcpy.CalculateField_management(clipwatIntProjected,waterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
    print "Calculated " + waterArea
except:
    arcpy.GetMessages()

# join waterArea to clipnetInt
try:
    joinTime = datetime.datetime.now()
    arcpy.JoinField_management(clipnetInt,INTRSCTID,clipwatIntProjected,INTRSCTID,waterArea)
    print "Joined " + waterArea + " to " + clipnetInt
    print datetime.datetime.now() - joinTime
except:
    arcpy.GetMessages()

# add and calculate the areakmmasked field
try:
    maskedFeatureArea = "AREAKMMASKED"
    arcpy.AddField_management(clipnetInt,maskedFeatureArea,'DOUBLE')
    arcpy.CalculateField_management(clipnetInt,maskedFeatureArea,'!' + featureArea + '! - !' + waterArea + "!",'PYTHON')
    print "calculated " + maskedFeatureArea
except:
    arcpy.GetMessages()


# define cntFields list.  this is a list of fields to be aggregated by adminID
cntFields = [[featureArea,'SUM'],[waterArea,'SUM'],[maskedFeatureArea,'SUM']]
joinCNTFields = ["SUM_" + featureArea]

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
   
    # add count field and calculate
    try:
        arcpy.AddField_management(clipnetInt,cntField,'Double')
        arcpy.AddField_management(clipnetInt,maskedCNTField,'Double')
        arcpy.CalculateField_management(clipnetInt,cntField,"!" + featureArea + "! * !"
                                        + dsField + "!","PYTHON")
        arcpy.CalculateField_management(clipnetInt,maskedCNTField,"!" + maskedFeatureArea + "! * !"
                                        + maskedDSField + "!","PYTHON")
        print "Calculated Population in " + cntField + " and " + maskedCNTField        
    except:
        arcpy.GetMessages()    
        
# Sum proportional allocation count fields 
sumTbl = inFC + "_aggregated_estimates"
pixelID = "PIXELID"
try:
    arcpy.Statistics_analysis(clipnetInt,sumTbl,cntFields,pixelID)
    arcpy.AddIndex_management(sumTbl,pixelID,pixelID + "_index","UNIQUE")    
    print "Calculated Statistics"    
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

print datetime.datetime.now() - startTime 
