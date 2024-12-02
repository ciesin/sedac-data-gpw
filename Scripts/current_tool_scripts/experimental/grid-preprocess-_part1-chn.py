# grid-preprocess.py
# execute intermediate gridding steps to calculate fields for gridding
# Kytt MacManus
# February 2, 2013

# import libraries
import arcpy, os, sys
import datetime

# helper method to join fields
def joinVariables(baseFeature,joinField,joinFeature,joinVariables):
    # Make Feature Layers
    layer1 = os.path.basename(baseFeature) + "_lyr"
    layer2 = os.path.basename(joinFeature) + "_lyr"
    try:
        addTime = datetime.datetime.now()
        if not arcpy.Exists(layer1):
            try:
                arcpy.MakeFeatureLayer_management(baseFeature,layer1)
            except:
                arcpy.MakeTableView_management(baseFeature,layer1)
        if not arcpy.Exists(layer2):
            try:
                arcpy.MakeFeatureLayer_management(joinFeature,layer2)
            except:
                arcpy.MakeTableView_management(joinFeature,layer2)
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
    for joinVariable in joinVariables:
        print joinVariable
        try:
            addTime = datetime.datetime.now()
            expression = '!' + os.path.basename(joinFeature) + "." + joinVariable + '!'
            arcpy.CalculateField_management(layer1,os.path.basename(baseFeature) + "." + joinVariable,expression,'PYTHON')
            print "Calculated " + joinVariable
            arcpy.AddMessage("Calculated " + joinVariable)
            print datetime.datetime.now() - addTime
            arcpy.AddMessage(datetime.datetime.now() - addTime)
        except:
            print arcpy.GetMessages()
    try:
        addTime = datetime.datetime.now()
        arcpy.RemoveJoin_management(layer1,os.path.basename(joinFeature))
        print "Removed temporary join"
        arcpy.Delete_management(layer1)
        arcpy.Delete_management(layer2)
        arcpy.AddMessage("Removed temporary join")
        print datetime.datetime.now() - addTime
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        print arcpy.GetMessages()


def main():
    startTime = datetime.datetime.now()
        
    # define inputs
    inFC = r'E:\gpw\chn\chn.gdb\chn_admin4_boundaries_2010' 
    waterExist = "true"
    grCalc = "true"
    workspace = r'E:\gpw\chn\chn.gdb'
    useISO = "true"

    # define workspace environment
    arcpy.env.workspace = workspace

    # define gridding resolution
    # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
    # 1 degree divided into 120 parts is 30 seconds
    linespd = 120
    ##linespd = arcpy.GetParameterAsText(1)

    # parse inFC to determine rootName
    if not useISO == "true":
         rNameParse = os.path.basename(inFC).split("_")
         rootName = rNameParse[0] + "_" + rNameParse[1]
    else:
        rootName = os.path.basename(inFC)[:3]
    arcpy.AddMessage(rootName)

    # define input fishnet
    inFish = rootName + "_fishnet"
    arcpy.AddMessage(inFish)
    # check to see that fishnet exists, if it doesn't kill the script
    if not arcpy.Exists(inFish):
        arcpy.AddMessage("The input fishnet does not exist, check the geodatabase")
        sys.exit("The input fishnet does not exist, check the geodatabase")

    # define estimatesTable
    estimatesTable = rootName + "_estimates"

    # first check that the UBID field exists in both the estimates and boundaries, if not exit
    if not len(arcpy.ListFields(inFC,"UBID"))==1:
        arcpy.AddMessage("The boundaries are missing UBID")
        sys.exit("The boundaries are missing UBID")
    elif not len(arcpy.ListFields(estimatesTable,"UBID"))==1:
        arcpy.AddMessage("The census data is missing UBID")
        sys.exit("The census data is missing UBID")         
    else:
        pass

    # check to see that estimates exists, if it doesn't kill the script
    if not arcpy.Exists(estimatesTable):
        arcpy.AddMessage("The input census estimates do not exist, check the geodatabase")
        sys.exit("The input census estimates do not exist, check the geodatabase")

    # define spatial reference
    prjFile = r'\\Dataserver0\gpw\GPW4\Gridding\country\custom_projections' + os.path.sep + rootName + "_mollweide.prj"
    # check to see that estimates exists, if it doesn't kill the script
    if not arcpy.Exists(prjFile):
        arcpy.AddMessage("The input prj file does not exist, check the network")
        sys.exit("The input prj file does not exist, check the network")
    else:
        spatialRef = open(prjFile,"r").read()

    #######################################################################################

    # make a copy of inFC
    inFCG = inFC + "_gridding"
    try:
        arcpy.Copy_management(inFC,inFCG)
        arcpy.AddMessage("Created " + inFCG)
    except:
        arcpy.GetMessages()
        
    # add a tmpid field and calculate it equal to the OBJECTID
    try:
        tmpid = "TEMPID"
        arcpy.AddField_management(inFCG,tmpid,'LONG','12')
        arcpy.CalculateField_management(inFCG,tmpid,'!OBJECTID!','PYTHON')
        arcpy.AddMessage("calculated " + tmpid)
    except:
        arcpy.GetMessages()    

    # project inFCG to mollweide
    try:
        projectFC = inFC + "_mollweide"
        arcpy.Project_management(inFCG, projectFC, spatialRef)
        arcpy.AddMessage("created " + projectFC)
    except:
        arcpy.GetMessages()

    # add ADMINAREAKM and calculate
    try:
        adminArea = "ADMINAREAKM"
        arcpy.AddField_management(projectFC,adminArea,'DOUBLE')
        arcpy.AddField_management(inFCG,adminArea,'DOUBLE')
        arcpy.CalculateField_management(projectFC,adminArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        arcpy.AddMessage("calculated " + adminArea)
    except:
        arcpy.GetMessages()

    # join ADMINAREAKM to inFCG
    try:
        joinTime = datetime.datetime.now()
        joinVariables(inFCG,tmpid,projectFC,[adminArea])
##        arcpy.JoinField_management(inFCG,tmpid,projectFC,tmpid,adminArea)
        arcpy.AddMessage("joined " + adminArea + " to " + inFCG)
        arcpy.AddMessage(datetime.datetime.now() - joinTime)
    except:
        arcpy.GetMessages()
       
    if waterExist == "true":
        # define input waterMask
        waterMask = rootName + "_water_mask"
        # check to see that waterMask exists, if it doesn't kill the script
        if not arcpy.Exists(waterMask):
            arcpy.AddMessage("The input water mask does not exist, but the parameter states that it should. Verify that it should or should not")        
            sys.exit("The input water mask does not exist, but the parameter states that it should. Verify that it should or should not")
        # clip inFC to waterMask
        waterFC = rootName + "_water_areas"
        try:
            arcpy.Clip_analysis(inFCG,waterMask,waterFC)
            arcpy.AddMessage("Created " + waterFC)
        except:
            arcpy.GetMessages
            
        # project waterFC to mollweide
        try:
            waterProjectFC = waterFC + "_mollweide"
            arcpy.Project_management(waterFC, waterProjectFC, spatialRef)
            arcpy.AddMessage("created " + waterProjectFC)
        except:
            arcpy.GetMessages()

        # add ADMINWATERAREAKM and calculate
        try:
            adminWaterArea = "ADMINWATERAREAKM"
            arcpy.AddField_management(waterProjectFC,adminWaterArea,'DOUBLE')
            arcpy.AddField_management(inFCG,adminWaterArea,'DOUBLE')
            arcpy.CalculateField_management(waterProjectFC,adminWaterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
            arcpy.AddMessage("calculated " + adminWaterArea)
        except:
            arcpy.GetMessages()


        # join ADMINWATERAREAKM to inFCG
        try:
            joinTime = datetime.datetime.now()
            joinVariables(inFCG,tmpid,waterProjectFC,[adminWaterArea])
##            arcpy.JoinField_management(inFCG,tmpid,waterProjectFC,tmpid,adminWaterArea)
            arcpy.AddMessage("joined " + adminWaterArea + " to " + inFCG)
            arcpy.AddMessage(datetime.datetime.now() - joinTime)
        except:
            arcpy.GetMessages()

        # Need to convert Nulls to Zeros
        try:
            adminWaterLYR = "adminwaterlyr"
            arcpy.MakeFeatureLayer_management(inFCG,adminWaterLYR,adminWaterArea + " IS NULL")
            arcpy.CalculateField_management(adminWaterLYR,adminWaterArea,0, "PYTHON")
            arcpy.AddMessage("Recoded Nulls")
        except:
            arcpy.GetMessages()
    else:
        # define input waterMask
        waterMask = rootName + "_water_mask"
        # check to see that waterMask exists, if it doesn't kill the script
        if arcpy.Exists(waterMask):
            arcpy.AddMessage("The input water mask exists, but the parameter states that it shouldn't. Verify that it should or should not")
            sys.exit("The input water mask exists, but the parameter states that it shouldn't. Verify that it should or should not")
        # add ADMINWATERAREAKM and calculate
        try:
            adminWaterArea = "ADMINWATERAREAKM"
            arcpy.AddField_management(inFCG,adminWaterArea,'DOUBLE')
            arcpy.CalculateField_management(inFCG,adminWaterArea,0,'PYTHON')
            arcpy.AddMessage("calculated " + adminWaterArea)
        except:
            arcpy.GetMessages()

    ## add ADMINAREAKMMASKED to inFCG and calculate
    try:
        maskedArea = "ADMINAREAKMMASKED"
        arcpy.AddField_management(inFCG,maskedArea,'DOUBLE')
        arcpy.CalculateField_management(inFCG,maskedArea,'!' + adminArea + '! - !' + adminWaterArea + "!",'PYTHON')
        arcpy.AddMessage("calculated " + maskedArea)
    except:
        arcpy.GetMessages()
        
    # Need to convert Negatives to Zeros
    try:
        adminMaskedLYR = "adminmaskedlyr"
        arcpy.MakeFeatureLayer_management(inFCG,adminMaskedLYR,maskedArea + " < 0")
        arcpy.CalculateField_management(adminMaskedLYR,maskedArea,0, "PYTHON")
        arcpy.AddMessage("Recoded Negatives")
    except:
        arcpy.GetMessages()

    # join fields from estimates table to inFCG
    # must first create a list of fields and append their names to fieldList
    if grCalc == "true":
        fieldList = []
        flds = arcpy.ListFields(estimatesTable,"*E_A*")
        for fld in flds:
            fieldList.append(fld.name)
            try:
                arcpy.AddField_management(inFCG,fld.name,'DOUBLE')
                arcpy.AddMessage("Added " + fld.name)
            except:
                arcpy.GetMessages()
    else:
        fieldList = []
        flds = arcpy.ListFields(estimatesTable,"A*2010*")
        for fld in flds:
            fieldList.append(fld.name)
            try:
                arcpy.AddField_management(inFCG,fld.name,'DOUBLE')
                arcpy.AddMessage("Added " + fld.name)
            except:
                arcpy.GetMessages()
        flds2 = arcpy.ListFields(estimatesTable,"UNE_A*")
        for fld2 in flds2:
            fieldList.append(fld2.name)
            try:
                arcpy.AddField_management(inFCG,fld2.name,'DOUBLE')
                arcpy.AddMessage("Added " + fld2.name)
            except:
                arcpy.GetMessages()
    # join estimates fields to inFCG
    try:
        joinTime = datetime.datetime.now()
        joinVariables(inFCG,"UBID",estimatesTable,fieldList)
##        arcpy.JoinField_management(inFCG,"UBID",estimatesTable,"UBID",fieldList)
        arcpy.AddMessage("joined estimates fields to " + inFCG)
        arcpy.AddMessage(datetime.datetime.now() - joinTime)
    except:
        arcpy.GetMessages()

    ### This section is adapted from calcdensities.py as written
    ### by Greg Yetman circa 2010
    # iterate estimates fields and calculate densities
    # Create a table view to avoid division by zero
    tblSel = rootName + '_tblSel'
    whereCls = adminArea + ' > 0'
    tblSel = arcpy.MakeTableView_management(inFCG,tblSel,whereCls)
    for field in fieldList:
        joinTime = datetime.datetime.now()
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
            arcpy.AddMessage("Calculated " + dsField)
            arcpy.CalculateField_management(tblSel,maskedDSField,exp2,'PYTHON')
            arcpy.AddMessage("Calculated " + maskedDSField)
            arcpy.AddMessage(datetime.datetime.now() - joinTime)
        except:
            arcpy.GetMessages()

    # clip the fishnet to the input fc extent        
    clipnet = inFC + "_fishnet_clipped"
    try:
        arcpy.Clip_analysis(inFish,inFCG,clipnet)
        arcpy.AddMessage('Clipped fishnet to ' + inFCG)
    except:
        arcpy.GetMessages()
        
    # intersect fishnet and inFCG
    clipnetInt = clipnet + "_intersect"
    inFeatures = [inFCG,clipnet]
    try:
        arcpy.Intersect_analysis(inFeatures, clipnetInt)
        arcpy.AddMessage('Intersected clipped fishnet and input features.')
    except:
        arcpy.GetMessages()

    # add and calculate another unique id field called INTRSCTID
    INTRSCTID = "INTRSCTID"
    try:
        arcpy.AddField_management(clipnetInt,INTRSCTID,'LONG')
        arcpy.CalculateField_management(clipnetInt,INTRSCTID,'!OBJECTID!','PYTHON')
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
        arcpy.Project_management(clipnetInt,clipnetIntProjected,spatialRef)
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
        arcpy.AddField_management(clipnetIntProjected,featureArea,'DOUBLE')
        arcpy.AddField_management(clipnetInt,featureArea,'DOUBLE')
        arcpy.CalculateField_management(clipnetIntProjected,featureArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        arcpy.AddMessage("Calculated " + featureArea)
    except:
        arcpy.GetMessages()

    # join featureArea to clipnetInt
    try:
        joinTime = datetime.datetime.now()
        joinVariables(clipnetInt,INTRSCTID,clipnetIntProjected,[featureArea])
##        arcpy.JoinField_management(clipnetInt,INTRSCTID,clipnetIntProjected,INTRSCTID,featureArea)
        arcpy.AddMessage("Joined " + featureArea + " to " + clipnetInt)
        arcpy.AddMessage(datetime.datetime.now() - joinTime)
    except:
        arcpy.GetMessages()

    if waterExist =="true":
        # clip clipnetInt to the waterMask extent        
        clipwatInt = inFC + "_water_mask_clipped_intersect"
        try:
            arcpy.Clip_analysis(clipnetInt,waterMask,clipwatInt)
            arcpy.AddMessage('Clipped fishnet to ' + waterMask)
        except:
            arcpy.GetMessages()
            
        # project clipwatInt to mollweideCustom
        try:        
            clipwatIntProjected = clipwatInt + '_projected'
            arcpy.Project_management(clipwatInt,clipwatIntProjected,spatialRef)    
            arcpy.AddMessage("Projected " + clipwatInt)
        except:
            arcpy.GetMessages()

        # add an area field to clipnetIntProjected
        waterArea = "WATERAREAKM"
        try:
            arcpy.AddField_management(clipwatIntProjected,waterArea,'DOUBLE')
            arcpy.AddField_management(clipnetInt,waterArea,'DOUBLE')
            arcpy.CalculateField_management(clipwatIntProjected,waterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
            arcpy.AddMessage("Calculated " + waterArea)
        except:
            arcpy.GetMessages()


    arcpy.AddMessage(datetime.datetime.now() - startTime)
if __name__ == '__main__':
    main()
