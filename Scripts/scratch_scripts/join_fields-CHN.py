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
    inFC = r'E:\gpw\chn\chn.gdb\chn_admin3_boundaries_2010'
    ##inFC = arcpy.GetParameterAsText(0)
    ##workspace = arcpy.GetParameterAsText(1)
    workspace = r'E:\gpw\chn\chn.gdb'
    waterExist = "true"#arcpy.GetParameterAsText(2)
    # define workspace environment
    arcpy.env.workspace = workspace
    # parse inFC to determine rootName
    rootName = os.path.basename(inFC)[:3]
    # make a copy of inFC
    inFCG = inFC + "_gridding"
    # intersect fishnet and inFCG
    clipnetInt = inFC + "_fishnet_clipped_intersect"
    # define estimatesTable
    estimatesTable = rootName + "_estimates"

    # join fields from estimates table to inFCG
    # must first create a list of fields and append their names to fieldList
    fieldList = []
    flds = arcpy.ListFields(inFCG,"*ATOT*2010*")###CHECK THIS
    for fld in flds:
        fieldList.append(fld.name)
        try:
##            joinTime = datetime.datetime.now()
##            arcpy.AddField_management(clipnetInt,fld.name,'DOUBLE')
            print "Added " + fld.name
##            print datetime.datetime.now() - joinTime
        except:
            arcpy.GetMessages()
    print fieldList

    # join ADMINAREAKM to inFCG
    try:
        joinTime = datetime.datetime.now()
        joinVariables(clipnetInt,"TEMPID",inFCG,fieldList)
        print "joined " 
        print datetime.datetime.now() - joinTime
    except:
        arcpy.GetMessages()

    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()

