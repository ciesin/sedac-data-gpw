# population-estimates.py
# produce population estimates
# Kytt MacManus
# 2-11-13

# import libraries
import os, arcpy, sys
import datetime

# set counter
startTime = datetime.datetime.now()

# define input table
##inTable = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\npl.gdb\npl_age_sex_proportions_2011"
inTable = arcpy.GetParameterAsText(0)
# define output workspace
##outWS = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\npl.gdb"
outWS = arcpy.GetParameterAsText(1)
# define growth rate table
##grTable = r"\\Dataserver0\gpw\GPW4\Gridding\Country\inputs\npl.gdb\npl_admin3_growth_rate"
grTable = arcpy.GetParameterAsText(2)
# define join field
##joinField = "UCID3"
joinField = arcpy.GetParameterAsText(3)
# define transfer attributes
attributes = ["YEARTO2000","YEARTO2005","YEARTO2010",
              "YEARTO2015","YEARTO2020","AGR"]

# check to see that attributes fields exist
for checkField in attributes:
    if not len(arcpy.ListFields(grTable,checkField))==1:
        arcpy.AddMessage(grTable + " is missing " + checkField + " check table and reprocess")
        sys.exit()

### LATER ADD FUNCTION TO CALCULATE YEARTO FIELDS IN SCRIPT

##        if checkField == "AGR":
##            arcpy.AddMessage("Check GR Table for AGR and Reprocess")
##            sys.exit()
##        else:
##            if not len(arcpy.ListFields(inTable,"CENSUSYEAR"))==1:
##                arcpy.AddMessage("CENSUSYEAR is missing from " + inTable + " check and reprocess")
##                sys.exit()
##            else:
##                yearsToAdd = ["YEARTO2000","YEARTO2005","YEARTO2010","YEARTO2015","YEARTO2020"]
##                for yearToAdd in yearsToAdd:
##                    # Add Field to 
            
        
    

##attributes = arcpy.GetParameterAsText(4)
# define outTable
outTable = outWS + os.sep + os.path.basename(inTable).replace(os.path.basename(inTable)[4:],"estimates")

# copy new table
try:
    arcpy.Copy_management(inTable,outTable)
    arcpy.AddMessage("Created " + outTable)
except:
    arcpy.GetMessages()
# join fields
try:
    arcpy.JoinField_management(outTable,joinField,grTable,joinField,attributes)
except:
    arcpy.GetMessages()
# define target years
targetYears = ["2000","2005","2010","2015","2020"]

# iterate again
for year in targetYears:
    arcpy.AddMessage("considering " + year)
    # perform estimates. first project the total population to the reference year
    # add field to outTable
    try:
        eField = "E_ATOTPOPBT_" + year
        arcpy.AddField_management(outTable,eField,"DOUBLE")
    except:
        arcpy.GetMessages()
    # construct calcExpression
    calcExpression = "!ATOTPOPBT! * math.exp( !AGR! * !YEARTO" + year + "! )"
    # perform calculation
    try:
        arcpy.CalculateField_management(outTable,eField,calcExpression,"PYTHON_9.3")
        arcpy.AddMessage("calculated " + eField)
    except:
        arcpy.GetMessages()
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
                arcpy.AddMessage("calculated " + newField)
            except:
                arcpy.GetMessages()
    ##        # delete proportion field
    ##        try:
    ##            arcpy.DeleteField_management(outTable,field)
    ##        except:
    ##            arcpy.GetMessages()
    arcpy.AddMessage("completed calculations")
        
arcpy.AddMessage(datetime.datetime.now() - startTime)  




    
    
