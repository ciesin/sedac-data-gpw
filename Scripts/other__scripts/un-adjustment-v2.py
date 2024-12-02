# un-adjustment.py
# produce un adjusted population estimates
# Kytt MacManus
# 2-1213

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

# binary flag to indicate whether growth rate has been calculated
grCalc = "true" #arcpy.GetParameterAsText(0)
# define input table
##inTable = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\npl.gdb\npl_estimates"
inTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\can_province\can.gdb\can_estimates"#arcpy.GetParameterAsText(1)
# define output workspace
##outWS = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\npl.gdb"
outWS = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\can_province\can.gdb"#arcpy.GetParameterAsText(2)
# define growth rate table
inUNTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\ancillary.gdb\un_adjustment_factors"
##grTable = arcpy.GetParameterAsTest(2)
# extract country specific data
iso = os.path.basename(inTable)[:3]
# select appropriate row
try:
    unTable = outWS + os.sep + iso + "_un_adjustment"
    arcpy.TableSelect_analysis(inUNTable,unTable,'"ISO" = ' + "'" + iso.upper() + "'")
    arcpy.AddMessage("Created " + unTable)
    print "Created " + unTable
except:
    print arcpy.GetMessages()

# create backup of inTable
try:
    backupTable = outWS + os.sep + iso + "_estimates_backup"
    arcpy.Copy_management(inTable,backupTable)
    arcpy.AddMessage("Created " + backupTable)
    print "Created " + backupTable
except:
    print arcpy.GetMessages()

# create list of total pop fields to summarize
if grCalc == "true":
    summaryFields = ["E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020"]
else:
    summaryFields = ["ATOTPOPBT"]
# create empty list of adjFields to add adjField values to
adjFields = []
# iterate and summarize
for summaryField in summaryFields:
    # define outTable
    outTable = "in_memory" + os.sep + iso + "_" + summaryField #
    # summarize the field
    try:
        arcpy.Frequency_analysis(inTable,outTable,"UCID0",summaryField)
        arcpy.AddMessage("Created " + outTable)
        print "Created " + outTable
    except:
        print arcpy.GetMessages()
    # join the summarized GPWPOP to the un adjustment table
    try:
        arcpy.JoinField_management(unTable,"UCID0",outTable,"UCID0",summaryField)
        arcpy.AddMessage("Joined Fields")
        print "Joined fields"
    except:
        print arcpy.GetMessages()
    # add adjustment factor field
    if grCalc == "true":
        adjField = "UNADJFAC_" + summaryField[-4:]
        numerator = "UNPOP" + summaryField[-4:]
    else:
        adjField = "UNADJFAC_2010"
        numerator = "UNPOP2010"
    adjFields.append(adjField)
    try:
        arcpy.AddField_management(unTable,adjField,"DOUBLE")
        arcpy.AddField_management(inTable,adjField,"DOUBLE")
        print "Added " + adjField
    except:
        print arcpy.GetMessages()
    # calculation adjustment factor field
    
    calcExpression = "(!" + numerator + "!/!" + summaryField + "!) - 1" 
    try:
        arcpy.CalculateField_management(unTable,adjField,calcExpression,"PYTHON_9.3")
        arcpy.AddMessage("Calculated " + adjField)
        print "Calculated " + adjField
    except:
        print arcpy.GetMessages()
# join adjustment factor fields to the btn_estimates table
try:
    joinVariables(inTable,"UCID0",unTable,adjFields)
##    arcpy.JoinField_management(inTable,"UCID0",unTable,"UCID0",adjFields)
    arcpy.AddMessage("Joined Fields")
    print "Joined Fields"
except:
    arcpy.GetMessages()
# iterate through adjFields
for adjField in adjFields:
    if grCalc == "true":
        year = adjField[-4:]
        # Create list of fields to adjust
        eFields = arcpy.ListFields(inTable,"E_*" + year)
        #
        newFieldPrefix = "UN"
        newFieldSuffix = ""
    else:
        year = "2010"
        # Create list of fields to adjust
        eFields = arcpy.ListFields(inTable,"A*")
        #
        newFieldPrefix = "UNE_"
        newFieldSuffix = "2010"
    # iterate the eFields
    for eField in eFields:
        fieldName = eField.name
        # define newField
        newField = newFieldPrefix + fieldName + newFieldSuffix
        # add newField to table
        try:            
            arcpy.AddField_management(inTable,newField,"DOUBLE")
            print "Added " + newField
        except:
            print arcpy.GetMessages()
        # construct unAdjustment
        unAdjustment = "(!" + adjField + "! * !" + fieldName + "!) + !" + fieldName + "!"
        # perform calculation
        try:
            arcpy.CalculateField_management(inTable,newField,unAdjustment,"PYTHON_9.3")
            arcpy.AddMessage("Calculated " + newField)
            print "Calculated " + newField
        except:
            print arcpy.GetMessages()
        
print datetime.datetime.now() - startTime  
