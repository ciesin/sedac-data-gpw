# GPW Age Aggregation
# Purpose: To Aggregate Single Year Age Data into Age Groups
# Kytt MacManus
# September 13, 2012

# Import Python Libraries
import arcpy, os
from arcpy import env

# helper method to check if a field exists in a fc
def check_for_field(featClass,fieldName):
    hasField = 0
    desc = arcpy.Describe(featClass)
    fields = desc.fields
    for field in fields:
        # check without case as ArcGIS is not case sensitive
        if field.name.upper() == fieldName.upper():
            hasField = 1
    return hasField

# Set Overwrite Output Environment
env.overwriteOutput = 1

# Define Workspace Variable
workspace = r'D:\gpw4\ECU\ecu-ingest.gdb'
#r'D:\gpw4\ecu\ecu_output.gdb'

# Set Workspace and Scratch Workspace Environments
env.workspace = workspace
env.scratchworkspace = workspace

# Define input tables
table = "ecu_2010_v2"
sqlTable = "SQLTABLE"
statsView = "STATSVIEW"
statsTable = "ecu_2010_agegroup_stats"
# Define final output table
mergeTable = "ecu_2010_merge"
# Define ageGroupField
ageGroupField = "AGEGROUP"
# Define newFields
newFields = ["RURALMALE","RURALFEMALE","RURALTOTAL","URBANMALE","URBANFEMALE",
             "URBANTOTAL","URMALETOTAL","URFEMALETOTAL","URMFTOTAL"]
# Define statsFields
statsFields = [["RURALMALE","SUM"],["RURALFEMALE","SUM"],["RURALTOTAL","SUM"],["URBANMALE","SUM"],
               ["URBANFEMALE","SUM"],["URBANTOTAL","SUM"],["URMALETOTAL","SUM"],["URFEMALETOTAL","SUM"],
               ["URMFTOTAL","SUM"]]
# Define caseFields
caseFields = ["AGEGROUP","UCADMIN3"]

# Add Field to Table
if check_for_field(table,ageGroupField)==0:
    try:
        arcpy.AddField_management(table,ageGroupField,"TEXT")
        print "Added new field: " + ageGroupField
    except:
        print arcpy.GetMessages()
else:
    print ageGroupField + " already exists"

# Define new Categories
ageGroups = ["0-4","5-9","10-14","15-19","20-24","25-29","30-34","35-39","40-44",
              "45-49","50-54","55-59","60-64","65-69","70-74","75-79","80-84",
              "85plus"]
# Iterate ageGroups
for ageGroup in ageGroups:
    print ageGroup
    if ageGroup == "85plus":
        upperLimit = 120
        i = 0
        sqlQuery = '"' + "Age" +'"' + " = '" + str(upperLimit) + "'"
        while i < 35:
            upperLimit = upperLimit - 1
            sqlQuery = sqlQuery + ' OR "' + "Age" +'"' + " = '" + str(upperLimit) + "'"
            i = i + 1
    else:
        parse1 = ageGroup.split("-")
        upperLimit = int(parse1[1])
        i = 0
        sqlQuery = '"' + "Age" +'"' + " = '" + str(upperLimit) + "'"
        while i < 4:
            upperLimit = upperLimit - 1
            sqlQuery = sqlQuery + ' OR "' + "Age" +'"' + " = '" + str(upperLimit) + "'"
            i = i + 1
    print sqlQuery
    # Create Table View of Census Values with SQLQuey
    try:
        arcpy.MakeTableView_management(table,sqlTable,sqlQuery)
        print "Made sqlTable"
    except:
        print arcpy.GetMessages()
    # Calculate AGEGROUP Field
    try:
        arcpy.CalculateField_management(sqlTable,ageGroupField,'"' + ageGroup + '"')
        print "Calculated field"
    except:
        print arcpy.GetMessages()
##    # Save Rows
##    outSQL = "ecu_census_" + str(upperLimit)
##    try:
##        arcpy.CopyRows_management(sqlTable, outSQL)
##    except:
##        print arcpy.GetMessages()
    # Delete sqlTable
    try:
        arcpy.Delete_management(sqlTable)
    except:
        print arcpy.GetMessages()
# Create Table View 
try:
    arcpy.MakeTableView_management(table,statsView,'"' + ageGroupField + '"' + " IS NOT NULL")
    print "Made statsView"
except:
    print arcpy.GetMessages()

# Statistics by age group
if arcpy.Exists(statsTable)==False:    
    try:
        arcpy.Statistics_analysis(statsView,statsTable,statsFields,caseFields)
        print "Created " + statsTable
    except:
        print arcpy.GetMessages()
else:
    print statsTable + " already exists"
# Add newFields to Stats Table, Calculate Them, and Delete sum_newfield
for newField in newFields:
    sumField = "SUM_" + newField
    try:
        arcpy.AddField_management(statsTable,newField,"LONG")
        print "Added " + newField
    except:
        print arcpy.GetMessages()
    try:
        arcpy.CalculateField_management(statsTable,newField,"[" + sumField + "]")
        print "Calculated " + newField
    except:
        print arcpy.GetMessages()
    try:
        arcpy.DeleteField_management(statsTable,sumField)
        print "Deleted " + sumField
    except:
        print arcpy.GetMessages()
# Handle FREQUENCY and AGE fields
try:
    arcpy.DeleteField_management(statsTable,"FREQUENCY")
    print "Deleted FREQUENCY Field"
except:
    print arcpy.GetMessages()
try:
    arcpy.AddField_management(statsTable,"AGE","TEXT")
    print "Added AGE Field"
except:
    print arcpy.GetMessages()
try:
    arcpy.CalculateField_management(statsTable,"AGE","[" + ageGroupField + "]")
    print "Calculated AGE Field"
except:
    print arcpy.GetMessages()


# Merge statsTable and Table
try:
    arcpy.Merge_management([table,statsTable],mergeTable)
    print "Created " + mergeTable
except:
    print arcpy.GetMessages()
    
