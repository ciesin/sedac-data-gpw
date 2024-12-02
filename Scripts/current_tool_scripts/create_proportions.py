# create_proportions.py
# Create Proportion Table of Age/Sex Distribution from input Census Data
# Kytt MacManus
# 2-6-2013

# Revised 8-23-13 to include function to create 5 year age groups for data
# that only has single year breakdowns

# import libraries
import arcpy, os
import datetime

arcpy.env.overwriteOutput = True

# set start time counter
startTime = datetime.datetime.now()

# define input table
inputTable = arcpy.GetParameterAsText(0)
##inputTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\per.gdb\per_census_2007_ingest"
outputTable = arcpy.GetParameterAsText(1)
##outputTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\per.gdb\per_estimates"
# define total population field
totalPop = arcpy.GetParameterAsText(2)
##totalPop = "ATOTPOPBT"

########## Optional Parameters for activating age group algorithm

# Define Boolean parameter about age group existence
calcAgeGroups = arcpy.GetParameterAsText(3)
##calcAgeGroups = "true"

# Define Highest Age
##highestAge = "98"
highestAge = arcpy.GetParameterAsText(4)

# create output table
try:
    vTable = os.path.basename(inputTable)[:3] + "_VIEW"
    vExpression = totalPop + " >= 0" 
    arcpy.MakeTableView_management(inputTable, vTable, vExpression)
    arcpy.CopyRows_management(vTable,outputTable)
##    arcpy.CopyRows_management(inputTable,outputTable)
    arcpy.AddMessage("Created " + outputTable)
##    print "Created " + outputTable
except:
    arcpy.AddMessage(arcpy.GetMessages())

# check to see if the script should create age groups
if calcAgeGroups == "true":
    # Define Field Acronyms
    # Insert logic to check which field acronyms are part of the set
    fieldPossibilities = ["FR","FU","FT","MR","MU","MT","BR","BU","BT"]
    fieldACRONYMS = []
    fieldList = []
    for fieldPossibility in fieldPossibilities:
        # Create list of fields with a given acronym
        fList = arcpy.ListFields(outputTable,"*" + fieldPossibility)
        # If the length of the field list is > 0, then add to the acronyms
        if len(fList)>0:
            fieldACRONYMS.append(fieldPossibility)
        else:
            arcpy.AddMessage(fieldPossibility + " does not exist in table")
    # Iterate
    for acronym in fieldACRONYMS:
        # Create List of AgeGroups
        ageGroups = ["A000_004","A005_009","A010_014","A015_019","A020_024",
                     "A025_029","A030_034","A035_039","A040_044","A045_049",
                     "A050_054","A055_059","A060_064","A065_069","A070_074",
                     "A075_079","A080_084","A085plus"]
        # Iterate
        for ageGroup in ageGroups:
            print "The age group is " + ageGroup
            arcpy.AddMessage("The age group is " + ageGroup)
            # Create routine to parse calculation expression
            ageGroupParts = ageGroup.split("_")
            if len(ageGroupParts)==2:
                beginningAgePart = ageGroupParts[0]
                beginningAge = beginningAgePart[1:]
                periodLength = 5
            else:
                beginningAge = "085"
                periodLength = int(highestAge) - 84 ###UPDATE AS NEEDED!!!!
            print "The beginning age is " + str(beginningAge) + " and the length of the period is " + str(periodLength)
            expression = "!A" + str(beginningAge) + acronym + "!"
            while periodLength > 1:
                if int(beginningAge)<10:
                    beginningAge = str(0)+str(0) + str(int(beginningAge) + 1)
                elif int(beginningAge)>9:
                    beginningAge = str(0) + str(int(beginningAge) + 1)
                expression = expression + " + !A" + str(beginningAge) + acronym + "!"
                periodLength = periodLength - 1
            print "The final expression is " + expression
            arcpy.AddMessage("The final expression is " + expression)
            
            # Define newField
            newField = ageGroup + acronym
            # Add newField to table
            try:
                arcpy.AddField_management(outputTable,newField,"DOUBLE")
                print "Added " + newField
            except:
                print arcpy.GetMessages()
                arcpy.AddMessage(arcpy.GetMessages())
            # Calculate newField
            try:
                arcpy.CalculateField_management(outputTable,newField,expression,"PYTHON")
                print "Calculated " + newField
                fieldList.append(newField)
                arcpy.AddMessage("Calculated " + newField)
            except:
                print arcpy.GetMessages()        
                arcpy.AddMessage(arcpy.GetMessages())
else:
    # list fields
    fieldList = arcpy.ListFields(inputTable,"A*")

# iterate
for fieldObject in fieldList:
    # create variable to hold field name
    try:
        field = fieldObject.name
    except:
        field = fieldObject
    if field == totalPop:
        pass
    else:
        # define the new proportion field
        newField = field + "_PROP"
        # add the new field to the output table
        try:
            arcpy.AddField_management(outputTable,newField,"DOUBLE")
##            arcpy.AddMessage("Added " + newField)
##            print "Added " + newField
        except:
            arcpy.AddMessage(arcpy.GetMessages())
        # create table view that controls for -9999 and division by 0
        # define view
        view = newField
        # define calculation expression
        expression = '"' + field + '" > 0 AND ' + '"' + field + '" <> 0'
        try:
            arcpy.MakeTableView_management(outputTable, view, expression)
##            arcpy.AddMessage("Created View: " + view)
##            print "Created View: " + view
        except:
            arcpy.AddMessage(arcpy.GetMessages())
        # calculate newField
        calculation = "!" + field + "! / !" + totalPop + "!"
        try:
            arcpy.CalculateField_management(view, newField, calculation, "PYTHON_9.3")
            arcpy.AddMessage("Calculated " + newField)
            print "Calculated " + newField
        except:
            arcpy.AddMessage(arcpy.GetMessages())
        # create table view to fill in nulls
        # define view
        view0 = newField + "0"
        # define calculation expression
        expression0 = '"' + newField + '" IS NULL ' 
        try:
            arcpy.MakeTableView_management(outputTable, view0, expression0)
##            arcpy.AddMessage("Created View: " + view0)
##            print "Created View: " + view0
        except:
            arcpy.AddMessage(arcpy.GetMessages())
        # calculate newField
        try:
            arcpy.CalculateField_management(view0, newField, "0", "PYTHON_9.3")
##            arcpy.AddMessage("Calculated Zeros in " + newField)
##            print "Calculated Zeros in " + newField
        except:
            arcpy.AddMessage(arcpy.GetMessages())
        # Delete input field which is no longer necessary
        try:
            arcpy.DeleteField_management(outputTable, field)
##            arcpy.AddMessage("Deleted " + field)
##            print "Deleted " + field
        except:
            arcpy.AddMessage(arcpy.GetMessages())
                                      
        
scriptTime = startTime - datetime.datetime.now()
arcpy.AddMessage("The script completed in: " + str(scriptTime))
##print "The script completed in: " + str(scriptTime)


