# population-estimates.py
# produce population estimates
# Kytt MacManus
# 2-11-13

# import libraries
import os, arcpy
import datetime

# set counter
startTime = datetime.datetime.now()
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
    for joinField in joinVariables:
        try:
            addTime = datetime.datetime.now()
            expression = '!' + os.path.basename(joinFeature) + "." + joinField + '!'
            arcpy.CalculateField_management(layer1,os.path.basename(baseFeature) + "." + joinField,expression,'PYTHON')
            print "Calculated " + joinField
            arcpy.AddMessage("Calculated " + joinField)
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
        
# define input table
inTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\fra.gdb\fra_proportions"
##inTable = arcpy.GetParameterAsText(0)
# define output workspace
outWS = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\fra.gdb"
##outWS = arcpy.GetParameterAsText(1)
# define growth rate table
grTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\fra.gdb\fra_growth_rate"
##grTable = arcpy.GetParameterAsTest(2)
# define join field
joinField = "USCID"
##joinField = arcpy.GetParameterAsText(3)
# define transfer attributes
attributes = ["YEARTO2000","YEARTO2005","YEARTO2010",
              "YEARTO2015","YEARTO2020","AGR"]
##attributes = arcpy.GetParameterAsText(4)
# define outTable
outTable = outWS + os.sep + os.path.basename(inTable).replace("_proportions",
                                                "_estimates")
# copy new table
try:
    arcpy.Copy_management(inTable,outTable)
    print outTable#test
except:
    arcpy.GetMessages()
    print arcpy.GetMessages()#test

# create field placeholders
for attribute in attributes:
    try:
        arcpy.AddField_management(outTable,attribute,"DOUBLE")
        print "Added " + attribute
    except:
        print arcpy.GetMessages()

# join fields
try:
    joinVariables(outTable,joinField,grTable,attributes)
##    arcpy.JoinField_management(outTable,joinField,grTable,joinField,attributes)
    print "Completed Joins"
except:
    print arcpy.GetMessages()
    
# define target years
targetYears = ["2000","2005","2010","2015","2020"]

# iterate again
for year in targetYears:
    print "considering " + year
    # perform estimates. first project the total population to the reference year
    # add field to outTable
    try:
        eField = "E_ATOTPOPBT_" + year
        arcpy.AddField_management(outTable,eField,"DOUBLE")
        print "Added " + eField
    except:
        print arcpy.GetMessages()
    # construct calcExpression
    calcExpression = "!ATOTPOPBT! * math.exp( !AGR! * !YEARTO" + year + "! )"
    # perform calculation
    try:
        arcpy.CalculateField_management(outTable,eField,calcExpression,"PYTHON_9.3")
        print "Calculated " + eField
    except:
        print arcpy.GetMessages()
    # if year is 2010, then perform age estimates by applying proportions
    if year == "2010":
        # list fields
        fieldList = arcpy.ListFields(outTable,"*PROP")
        # iterate fields
        for fld in fieldList:
            field = fld.name
            # define newField
            newField = "E_" + field.replace("PROP",year)
            # add newField
            try:
                arcpy.AddField_management(outTable,newField,"DOUBLE")
            except:
                arcpy.GetMessages()
            # define calculation expression
            propCalc = "!" + eField + "! * !" + field + "!"
            # perform calculation
            try:
                arcpy.CalculateField_management(outTable,newField,propCalc,"PYTHON_9.3")
            except:
                arcpy.GetMessages()
    ##        # delete proportion field
    ##        try:
    ##            arcpy.DeleteField_management(outTable,field)
    ##        except:
    ##            arcpy.GetMessages()
    print "completed calculations"
        
print datetime.datetime.now() - startTime  




    
    
