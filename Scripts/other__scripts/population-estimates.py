# population-estimates.py
# produce population estimates
# Kytt MacManus
# 2-11-13

# import libraries
import os, arcpy
import datetime

# set counter
startTime = datetime.datetime.now()

# define input table
inTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\per.gdb\per_proportions"
##inTable = arcpy.GetParameterAsText(0)
# define output workspace
outWS = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\per.gdb"
##outWS = arcpy.GetParameterAsText(1)
# define growth rate table
grTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\per.gdb\per_growth_rate"
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
                                                "estimates")
# copy new table
try:
    arcpy.Copy_management(inTable,outTable)
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
    print "considering " + year
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
            except:
                arcpy.GetMessages()
    ##        # delete proportion field
    ##        try:
    ##            arcpy.DeleteField_management(outTable,field)
    ##        except:
    ##            arcpy.GetMessages()
    print "completed calculations"
        
print datetime.datetime.now() - startTime  




    
    
