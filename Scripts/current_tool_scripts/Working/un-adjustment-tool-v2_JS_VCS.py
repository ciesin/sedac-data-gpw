# un-adjustment.py
# produce un adjusted population estimates
# Kytt MacManus
# 2-1213

# import libraries
import os, arcpy, sys
import datetime

# set counter
startTime = datetime.datetime.now()
# binary flag to indicate whether growth rate has been calculated
grCalc = "true"
# define input table
inTable = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\vcs.gdb\vcs_estimates"

# define output workspace
outWS = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\vcs.gdb"

# define growth rate table
inUNTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\ancillary.gdb\un_adjustment_factors"
##grTable = arcpy.GetParameterAsTest(2)
# extract country specific data
iso = "vcs"
uniso = "vat"
# select appropriate row
try:
    unTable = outWS + os.sep + iso + "_un_adjustment"
    arcpy.TableSelect_analysis(inUNTable,unTable,'"ISO" = ' + "'" + uniso.upper() + "'")
    #arcpy.AddMessage("Created " + unTable)
    print "Created " + unTable
except:
    print "Could not create table"

# create backup of inTable
try:
    backupTable = outWS + os.sep + iso + "_estimates_backup"
    arcpy.Copy_management(inTable,backupTable)
    #arcpy.AddMessage("Created " + backupTable)
    print "Created " + backupTable
except:
    print "Could not create backup table"

# create list of total pop fields to summarize
if grCalc == "true":
    print "Growth rate is true"
    summaryFields = ["E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020"]
else:
    sys.exit()
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
        print "Could not add fields to UN Table"
    # calculation adjustment factor field
    
    calcExpression = "(!" + numerator + "!/!" + summaryField + "!) - 1" 
    try:
        arcpy.CalculateField_management(unTable,adjField,calcExpression,"PYTHON_9.3")
        arcpy.AddMessage("Calculated " + adjField)
        print "Calculated adjField"
    except:
        print "Could not calculate adjField"
# join adjustment factor fields to the btn_estimates table
try:
    arcpy.JoinField_management(inTable,"UCID0",unTable,"UCID0",adjFields)
    print "Joined fields"
except Exception as e:
    print "Could not join fields"
    print e.message
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
