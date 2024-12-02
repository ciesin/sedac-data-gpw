# GPW Age Aggregation
# Purpose: To Aggregate Single Year Age Data into 5 Year Age Groups
# Kytt MacManus
# September 4, 2012

# Import Python Libraries
import arcpy, os
from arcpy import env

# Set Overwrite Output Environment
env.overwriteOutput = 1

# Define input table
table = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\per.gdb\per_census_2007_ingest'
##table = arcpy.GetParameterAsText(0)
# Define Highest Age
highestAge = "98"
##highestAge = arcpy.GetParameterAsText(0)

# Define Field Acronyms
fieldACRONYMS = ["FR","FU","FT","MR","MU","MT","BR","BU","BT"]

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
        
##        # Define newField
##        newField = ageGroup + acronym
##        # Add newField to table
##        try:
##            arcpy.AddField_management(table,newField,"DOUBLE")
##            print "Added " + newField
##        except:
##            print arcpy.GetMessages()
##            arcpy.AddMessage(arcpy.GetMessages())
##        # Calculate newField
##        try:
##            arcpy.CalculateField_management(table,newField,expression,"PYTHON")
##            print "Calculated " + newField
##            arcpy.AddMessage("Calculated " + newField)
##        except:
##            print arcpy.GetMessages()        
##            arcpy.AddMessage(arcpy.GetMessages())
