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
        arcpy.AddMessage("Removed temporary join")
        print datetime.datetime.now() - addTime
        arcpy.AddMessage(datetime.datetime.now() - addTime)
    except:
        print arcpy.GetMessages()


def main():
    startTime = datetime.datetime.now()
        
    # define inputs
    inFC = r'D:\GPW\aus\aus.gdb\aus_admin5_boundaries_2010'
    ##inFC = arcpy.GetParameterAsText(0)
    ##workspace = arcpy.GetParameterAsText(1)
    workspace = r'D:\GPW\aus\aus.gdb'
    waterExist = "true"#arcpy.GetParameterAsText(2)

    # define workspace environment
    arcpy.env.workspace = workspace

    # define gridding resolution
    # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
    # 1 degree divided into 120 parts is 30 seconds
    linespd = 120
    ##linespd = arcpy.GetParameterAsText(1)

    # parse inFC to determine rootName
    rootName = os.path.basename(inFC)[:3]

##    # define input fishnet
##    inFish = rootName + "_fishnet"
##
##    # check to see that fishnet exists, if it doesn't kill the script
##    if not arcpy.Exists(inFish):
##        arcpy.AddMessage("The input fishnet does not exist, check the geodatabase")
##        sys.exit("The input fishnet does not exist, check the geodatabase")

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
##        arcpy.Copy_management(inFC,inFCG)
        print "Created " + inFCG
    except:
        arcpy.GetMessages()
        

    # join fields from estimates table to inFCG
    # must first create a list of fields and append their names to fieldList
    fieldList = []
    flds = arcpy.ListFields(estimatesTable,"*E_ATOT*")###CHECK THIS
    for fld in flds:
        fieldList.append(fld.name)
        try:
##            arcpy.AddField_management(inFCG,fld.name,'DOUBLE')
            print "Added " + fld.name
        except:
            arcpy.GetMessages()
    # join estimates fields to inFCG
    try:
        joinTime = datetime.datetime.now()
##        joinVariables(inFCG,"UBID",estimatesTable,fieldList)
        print "joined estimates fields to " + inFCG
        print datetime.datetime.now() - joinTime
    except:
        arcpy.GetMessages()

    ### This section is adapted from calcdensities.py as written
    ### by Greg Yetman circa 2010
    # iterate estimates fields and calculate densities
    # Create a table view to avoid division by zero
    adminArea = "ADMINAREAKM"
    maskedArea = "ADMINAREAKMMASKED"
    tblSel = rootName + '_tblSel'
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
            joinTime = datetime.datetime.now()
            arcpy.CalculateField_management(tblSel,dsField,exp,'PYTHON')
            print "Calculated " + dsField
            arcpy.CalculateField_management(tblSel,maskedDSField,exp2,'PYTHON')
            print "Calculated " + maskedDSField
            print datetime.datetime.now() - joinTime
        except:
            arcpy.GetMessages()


    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()
