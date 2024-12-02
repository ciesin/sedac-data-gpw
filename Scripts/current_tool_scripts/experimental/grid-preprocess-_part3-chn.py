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
##    inFC = r'D:\GPW\mar.gdb\mar_admin3_boundaries_2010'
    inFC = r'E:\gpw\chn\chn.gdb\chn_admin4_boundaries_2010'
    
##    workspace = r'D:\GPW\mar.gdb'
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
    # parse inFC to determine rootName
    if not useISO == "true":
         rNameParse = os.path.basename(inFC).split("_")
         rootName = rNameParse[0] + "_" + rNameParse[1]
    else:
        rootName = os.path.basename(inFC)[:3]
    arcpy.AddMessage(rootName)

    # define input fishnet
    inFish = rootName + "_fishnet_v0"
    print inFish

    # define estimatesTable
    estimatesTable = rootName + "_estimates"

    # define spatial reference
    prjFile = r'\\Dataserver0\gpw\GPW4\Gridding\country\custom_projections' + os.path.sep + rootName + "_mollweide.prj"
    # check to see that estimates exists, if it doesn't kill the script
    if not arcpy.Exists(prjFile):
        arcpy.AddMessage("The input prj file does not exist, check the network")
        sys.exit("The input prj file does not exist, check the network")
    else:
        spatialRef = open(prjFile,"r").read()

    #######################################################################################

    # define inFC
    inFCG = inFC + "_gridding"
    tmpid = "TEMPID"
    projectFC = inFC + "_mollweide"
    adminArea = "ADMINAREAKM"
    waterMask = rootName + "_water_mask"
    waterFC = rootName + "_water_areas"
    waterProjectFC = waterFC + "_mollweide"
    adminWaterArea = "ADMINWATERAREAKM"
    adminWaterLYR = "adminwaterlyr"
    maskedArea = "ADMINAREAKMMASKED"
    adminMaskedLYR = "adminmaskedlyr"
    clipnet = inFC + "_fishnet_clipped"
    clipnetInt = clipnet + "_intersect"
    INTRSCTID = "INTRSCTID"
    featureArea = "AREAKM"
    waterArea = "WATERAREAKM"
    

    # join fields from estimates table to inFCG
    # must first create a list of fields and append their names to fieldList
    if grCalc == "true":
        fieldList = []
        flds = arcpy.ListFields(estimatesTable,"*E_A*")
        for fld in flds:
            fieldList.append(fld.name)
    else:
        fieldList = []
        flds = arcpy.ListFields(estimatesTable,"A*2010*")
        for fld in flds:
            fieldList.append(fld.name)
        flds2 = arcpy.ListFields(estimatesTable,"UNE_A*")
        for fld2 in flds2:
            fieldList.append(fld2.name)
        
    # add and calculate the areakmmasked field
    try:
        addTime = datetime.datetime.now()
        maskedFeatureArea = "AREAKMMASKED"
        arcpy.AddField_management(clipnetInt,maskedFeatureArea,'DOUBLE')
        arcpy.CalculateField_management(clipnetInt,maskedFeatureArea,'!' + featureArea + '! - !' + waterArea + "!",'PYTHON')
        print "calculated " + maskedFeatureArea
        arcpy.AddMessage("Calculated " + maskedFeatureArea)
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        arcpy.GetMessages()
    # Need to convert Negatives to Zeros
    try:
        maskedLYR = rootName + "_maskedlyr"
        arcpy.MakeFeatureLayer_management(clipnetInt,maskedLYR,maskedFeatureArea + " < 0.0000001")
        arcpy.CalculateField_management(maskedLYR,maskedFeatureArea,0, "PYTHON")
        arcpy.AddMessage("Recoded Negatives")
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        arcpy.GetMessages()

    # Create In_memory Fishnet
    fishnet = r"E:\gpw\chn\chn.gdb" + os.sep + rootName + "_fishnet"
    try:
        addTime = datetime.datetime.now()
##        arcpy.CopyFeatures_management(inFish, fishnet)
        print "Created " + fishnet
        print datetime.datetime.now() - addTime
        arcpy.AddMessage("Created " + fishnet)
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        print arcpy.GetMessages()
    
    # define cntFields list.  this is a list of fields to be aggregated by adminID
    cntFields = [[featureArea,'SUM'],[waterArea,'SUM'],[maskedFeatureArea,'SUM']]
    joinCNTFields = ["SUM_" + featureArea, "SUM_" + waterArea, "SUM_" + maskedFeatureArea]
    for newField in joinCNTFields:
        addTime = datetime.datetime.now()
        try:
##            arcpy.AddField_management(fishnet,newField,"DOUBLE")
            print "Added " + newField
            arcpy.AddMessage("Added " + newField)
        except:
            print arcpy.GetMessages()
    arcpy.AddMessage("Added fields")
    arcpy.AddMessage(datetime.datetime.now() - addTime)

    # iterate the fields list to calculate counts
    for field in fieldList:
        addTime = datetime.datetime.now()
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
        try:
            arcpy.AddField_management(fishnet,"SUM_" + cntField,"DOUBLE")
            print "Added SUM_" + cntField
        except:
            print arcpy.GetMessages()
        joinCNTFields.append("SUM_" + maskedCNTField)
        try:
            arcpy.AddField_management(fishnet,"SUM_" + maskedCNTField,"DOUBLE")
            print "Added SUM_" + maskedCNTField
        except:
            print arcpy.GetMessages()
       
        # add count field and calculate
        try:
            arcpy.AddField_management(clipnetInt,cntField,'Double')
            arcpy.AddField_management(clipnetInt,maskedCNTField,'Double')
            arcpy.CalculateField_management(clipnetInt,cntField,"!" + featureArea + "! * !"
                                            + dsField + "!","PYTHON")
            arcpy.CalculateField_management(clipnetInt,maskedCNTField,"!" + maskedFeatureArea + "! * !"
                                            + maskedDSField + "!","PYTHON")
            print "Calculated Population in " + cntField + " and " + maskedCNTField
            arcpy.AddMessage("Calculated Population in " + cntField + " and " + maskedCNTField)
            arcpy.AddMessage(datetime.datetime.now() - addTime)
        except:
            arcpy.GetMessages()    
            
    # Sum proportional allocation count fields 
    sumTbl = rootName + "_aggregated_estimates"
    pixelID = "PIXELID"
    try:
        addTime = datetime.datetime.now()
        arcpy.Statistics_analysis(clipnetInt,sumTbl,cntFields,pixelID)
        arcpy.AddIndex_management(sumTbl,pixelID,pixelID + "_index","UNIQUE")    
        print "Calculated Statistics"
        arcpy.AddMessage("Calculated Statistics")
        arcpy.AddMessage(datetime.datetime.now() - addTime)        
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
        joinVariables(fishnet,"PIXELID",sumTbl,joinCNTFields)
##        arcpy.JoinField_management(inFish,"PIXELID",sumTbl,"PIXELID",joinCNTFields)
        print "Joined Statistic Fields to " + fishnet
        print datetime.datetime.now() - joinTime
    except:
        arcpy.GetMessages()
##    # copy in_memory version back to disk
##    outFish1 = rootName + "_fishnet_v0"
##    outFish = rootName + "_fishnet"
##    try:
##        addTime = datetime.datetime.now()
##        arcpy.Rename_management(inFish,outFish1)
##        arcpy.CopyFeatures_management(fishnet, outFish)
##        arcpy.Delete_management(fishnet)
##        print "Created " + outFish
##        print datetime.datetime.now() - addTime
##        arcpy.AddMessage("Created " + outFish)
##        arcpy.AddMessage(datetime.datetime.now() - addTime)
##    except:
##        print arcpy.GetMessages()


    arcpy.AddMessage(datetime.datetime.now() - startTime)
if __name__ == '__main__':
    main()
