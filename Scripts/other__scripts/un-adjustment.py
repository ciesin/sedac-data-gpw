# un-adjustment.py
# produce un adjusted population estimates
# Kytt MacManus
# 2-1213

# import libraries
import os, arcpy
import datetime

# set counter
startTime = datetime.datetime.now()

# define input table
inTable = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\npl.gdb\npl_estimates"
##inTable = arcpy.GetParameterAsText(0)
# define output workspace
outWS = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\npl.gdb"
##outWS = arcpy.GetParameterAsText(1)
# define growth rate table
unTable = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\npl.gdb\npl_un_adjustment"
##grTable = arcpy.GetParameterAsTest(2)
# create list of total pop fields to summarize
summaryFields = ["E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020"]
# create empty list of adjFields to add adjField values to
adjFields = []
# iterate and summarize
for summaryField in summaryFields:
    # define outTable
    outTable = "in_memory" + os.sep + summaryField #
    # summarize the field
    try:
        arcpy.Frequency_analysis(inTable,outTable,"UCID0",summaryField)
    except:
        arcpy.GetMessages()
    # join the summarized GPWPOP to the un adjustment table
    try:
        arcpy.JoinField_management(unTable,"UCID0",outTable,"UCID0",summaryField)
    except:
        arcpy.GetMessages()
    # add adjustment factor field
    adjField = "UNADJFAC_" + summaryField[-4:]
    adjFields.append(adjField)
    try:
        arcpy.AddField_management(unTable,adjField,"DOUBLE")
    except:
        arcpy.GetMessages()
    # calculation adjustment factor field
    numerator = "UNPOP" + summaryField[-4:]
    calcExpression = "(!" + numerator + "!/!" + summaryField + "!) - 1" 
    try:
        arcpy.CalculateField_management(unTable,adjField,calcExpression,"PYTHON_9.3")
    except:
        arcpy.GetMessages()
# join adjustment factor fields to the btn_estimates table
try:
    arcpy.JoinField_management(inTable,"UCID0",unTable,"UCID0",adjFields)
except:
    arcpy.GetMessages()
# iterate through adjFields
for adjField in adjFields:
    year = adjField[-4:]
    # Create list of fields to adjust
    eFields = arcpy.ListFields(inTable,"E_*" + year)
    # iterate the eFields
    for eField in eFields:
        fieldName = eField.name
        # define newField
        newField = "UN" + fieldName
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
        except:
            arcpy.GetMessages()
        
print datetime.datetime.now() - startTime  
