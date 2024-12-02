# un-adjustment.py
# produce un adjusted population estimates
# Kytt MacManus
# 2-1213

# import libraries
import os, arcpy
import datetime

# set counter
startTime = datetime.datetime.now()
# binary flag to indicate whether growth rate has been calculated
grCalc = "true"
# define input table
inTable = r"\\\\Dataserver0\gpw\GPW4\Gridding\country\inputs\sle.gdb\SLE_estimates"
inTable = arcpy.GetParameterAsText(1)
# define output workspace
outWS = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\sle.gdb"
outWS = arcpy.GetParameterAsText(2)
# define growth rate table
inUNTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\ancillary.gdb\un_adjustment_factors"
grTable = "true"
# extract country specific data
iso = os.path.basename(inTable)[:3]
# select appropriate row
try:
    unTable = outWS + os.sep + iso + "_un_adjustment"
    arcpy.TableSelect_analysis(inUNTable,unTable,'"ISO" = ' + "'" + iso.upper() + "'")
    arcpy.AddMessage("Created " + unTable)
except:
    arcpy.GetMessages()

# create backup of inTable
try:
    backupTable = outWS + os.sep + iso + "_estimates_backup"
    arcpy.Copy_management(inTable,backupTable)
    arcpy.AddMessage("Created " + backupTable)
except:
    arcpy.GetMessages()

# create list of total pop fields to summarize
if grCalc == "true":
    summaryFields = ["E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020"]
else:
    # In this case we are only grabbing the total pop BT for the year 2010.  We must revisit these countries to calculate GR,
    # at that point we will grid additional variables.
    arcpy.AddField_management(inTable,"ATOTPOPBT_2010","DOUBLE")
    arcpy.CalculateField_management(inTable,"ATOTPOPBT_2010","!ATOTPOPBT!","PYTHON")
    summaryFields = ["ATOTPOPBT_2010"]
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
    except:
        arcpy.GetMessages()
    # join the summarized GPWPOP to the un adjustment table
    try:
        arcpy.JoinField_management(unTable,"UCID0",outTable,"UCID0",summaryField)
        arcpy.AddMessage("Joined Fields")
    except:
        arcpy.GetMessages()
    # add adjustment factor field
##    if grCalc == "true":
    adjField = "UNADJFAC_" + summaryField[-4:]
    numerator = "UNPOP" + summaryField[-4:]
##    else:
##        adjField = "UNADJFAC_2010"
##        numerator = "UNPOP2010"
    adjFields.append(adjField)
    try:
        arcpy.AddField_management(unTable,adjField,"DOUBLE")
        
    except:
        arcpy.GetMessages()
    # calculation adjustment factor field
    
    calcExpression = "(!" + numerator + "!/!" + summaryField + "!) - 1" 
    try:
        arcpy.CalculateField_management(unTable,adjField,calcExpression,"PYTHON_9.3")
        arcpy.AddMessage("Calculated " + adjField)
    except:
        arcpy.GetMessages()
# join adjustment factor fields to the btn_estimates table
try:
    arcpy.JoinField_management(inTable,"UCID0",unTable,"UCID0",adjFields)
    arcpy.AddMessage("Joined Fields")
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
    else:
        year = "2010"
        # Create list of fields to adjust
        eFields = arcpy.ListFields(inTable,"A*2010*")
        #
        newFieldPrefix = "UNE_"        
    # iterate the eFields
    for eField in eFields:
        fieldName = eField.name
        # define newField
        newField = newFieldPrefix + fieldName
        # add newField to table
        try:            
            arcpy.AddField_management(inTable,newField,"DOUBLE")
        except:
            arcpy.GetMessages()
        # construct unAdjustment
        unAdjustment = "(!" + adjField + "! * !" + fieldName + "!) + !" + fieldName + "!"
        # perform calculation
        try:
            arcpy.CalculateField_management(inTable,newField,unAdjustment,"PYTHON_9.3")
            arcpy.AddMessage("Calculated " + newField)
        except:
            arcpy.GetMessages()
        
print datetime.datetime.now() - startTime  
