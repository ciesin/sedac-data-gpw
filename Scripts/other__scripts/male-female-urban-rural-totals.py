# GPW Age Aggregation
# Purpose: To Aggregate Males and Females into Totals by Urban Rural Classification
# Kytt MacManus
# September 4, 2012

# Import Python Libraries
import arcpy, os
from arcpy import env

# Set Overwrite Output Environment
env.overwriteOutput = 1

# Define Workspace Variable
workspace = r'\\DATASERVER0\gpw\GPW4\Working\Merge\SLV\Staging\SLV_2007_census.gdb'

# Set Workspace and Scratch Workspace Environments
env.workspace = workspace
env.scratchworkspace = workspace

# Define input table
table = "SLV_2007_age_sex_ur_1"

# Define Field Acronyms
fieldACRONYMS = ["FT"]#["FR","FU","FT"]#,"MR","MU","MT"]

# Iterate
for acronym in fieldACRONYMS:
    # Create list of fields
    fields = arcpy.ListFields(table,"*PLUS" + acronym)    
    # Iterate fields
    for field in fields:
        fieldName = field.name
        print "Evaluating " + fieldName
        if fieldName[-2:] == "FR":
            newField = fieldName.replace(acronym,"RT")
        elif fieldName[-2:] == "FU":
            newField = fieldName.replace(acronym,"UT")
        elif fieldName[-2:] == "FT":
            newField = fieldName.replace(acronym,"T")
        print "The new field is " + newField
        maleField = fieldName.replace("F","M")
        expression = "!" + fieldName + "! + !" + maleField + "!"
        print "The calculation expression is " + expression 
        # Add newField to table
        try:
            arcpy.AddField_management(table,newField,"DOUBLE")
            print "Added " + newField
        except:
            print arcpy.GetMessages()
        # Calculate newField
        try:
            arcpy.CalculateField_management(table,newField,expression,"PYTHON")
            print "Calculated " + newField
        except:
            print arcpy.GetMessages()
        





### Create List Wildcards
##wildcards = ["A*FR"]#,"A*FU","A*FT","A*MR","A*MU","A*MT"]
##


