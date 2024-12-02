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
processTime = datetime.datetime.now()

# define input table
##inputTable = arcpy.GetParameterAsText(0)
inputTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\blz.gdb\blz_admin1_2010_input_population"
iso = os.path.basename(inputTable)[:3]
# define grTable
##grTable = arcpy.GetParameterAsText(1)
grTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\blz.gdb\blz_growth_rate_admin1"
# define grJoin
##grJoin = arcpy.GetParameterAsText(1)
grJoin = "USCID"
proportionsTable = inputTable.replace(os.path.basename(inputTable),iso + "_proportions")
estimatesTable = inputTable.replace(os.path.basename(inputTable),iso + "_estimates")
# define total population field
##totalPop = arcpy.GetParameterAsText()#DROP
totalPop = "ATOTPOPBT"
# define transfer attributes
attributes = ["YEARTO2000","YEARTO2005","YEARTO2010",
              "YEARTO2015","YEARTO2020","AGR"]
# define UN growth rate table
inUNTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\ancillary.gdb\un_adjustment_factors"

# create output table
try:
    vTable = iso + "_VIEW"
    vExpression = totalPop + " >= 0" 
    arcpy.MakeTableView_management(inputTable, vTable, vExpression)
    arcpy.CopyRows_management(vTable,proportionsTable)
##    arcpy.CopyRows_management(inputTable,proportionsTable)
    arcpy.AddMessage("Created " + proportionsTable)
    print "Created " + proportionsTable
except:
    print arcpy.GetMessages()
    arcpy.AddMessage(arcpy.GetMessages())

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
            arcpy.AddField_management(proportionsTable,newField,"DOUBLE")
            arcpy.AddMessage("Added " + newField)
            print "Added " + newField
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
        # create table view that controls for -9999 and division by 0
        # define view
        view = newField
        # define calculation expression
        expression = '"' + field + '" > 0 AND ' + '"' + field + '" <> 0'
        try:
            arcpy.MakeTableView_management(proportionsTable, view, expression)
            arcpy.AddMessage("Created View: " + view)
            print "Created View: " + view
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
        # calculate newField
        calculation = "!" + field + "! / !" + totalPop + "!"
        try:
            arcpy.CalculateField_management(view, newField, calculation, "PYTHON_9.3")
            arcpy.AddMessage("Calculated " + newField)
            print "Calculated " + newField
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
        # create table view to fill in nulls
        # define view
        view0 = newField + "0"
        # define calculation expression
        expression0 = '"' + newField + '" IS NULL ' 
        try:
            arcpy.MakeTableView_management(proportionsTable, view0, expression0)
            arcpy.AddMessage("Created View: " + view0)
            print "Created View: " + view0
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
        # calculate newField
        try:
            arcpy.CalculateField_management(view0, newField, "0", "PYTHON_9.3")
            arcpy.AddMessage("Calculated Zeros in " + newField)
            print "Calculated Zeros in " + newField
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
        # Delete input field which is no longer necessary
        try:
            arcpy.DeleteField_management(proportionsTable, field)
            arcpy.AddMessage("Deleted " + field)
            print "Deleted " + field
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
print "Completed proportions in " + str(datetime.datetime.now()-processTime)
######## START GROWTH RATE ESTIMATES
processTime = datetime.datetime.now()
# copy proportions table to create estimatesTable
try:
    arcpy.Copy_management(proportionsTable,estimatesTable)
    arcpy.AddMessage("Created " + estimatesTable)
    print "Created " + estimatesTable
except:
    print arcpy.GetMessages()
    arcpy.AddMessage(arcpy.GetMessages())
# join fields
try:
    arcpy.JoinField_management(estimatesTable,grJoin,grTable,grJoin,attributes)
    print "Joined GR Fields"
    arcpy.AddMessage("Joined GR Fields")
except:
    print arcpy.GetMessages()
    arcpy.AddMessage(arcpy.GetMessages())
# define target years
targetYears = ["2000","2005","2010","2015","2020"]
# iterate again
for year in targetYears:
    arcpy.AddMessage("considering " + year)
    print "considering " + year
    # perform estimates. first project the total population to the reference year
    # add field to estimatesTable
    try:
        eField = "E_ATOTPOPBT_" + year
        arcpy.AddField_management(estimatesTable,eField,"DOUBLE")
        print "Added " +  eField
    except:
        print arcpy.GetMessages()
        arcpy.AddMessage(arcpy.GetMessages())
    # construct calcExpression
    calcExpression = "!ATOTPOPBT! * math.exp( !AGR! * !YEARTO" + year + "! )"
    # perform calculation
    try:
        arcpy.CalculateField_management(estimatesTable,eField,calcExpression,"PYTHON_9.3")
        arcpy.AddMessage("Calculated " + eField)
        print "Calculated " + eField
    except:
        print arcpy.GetMessages()
        arcpy.AddMessage(arcpy.GetMessages())
    # if year is 2010, then perform age estimates by applying proportions
    if year == "2010":
        # list fields
        fieldList = arcpy.ListFields(estimatesTable,"*PROP")
        # iterate fields
        for fld in fieldList:
            field = fld.name
            # define newField
            newField = "E_" + field.replace("PROP",year)
            # add newField
            try:
                arcpy.AddField_management(estimatesTable,newField,"DOUBLE")
                print "Added " + newField
            except:
                print arcpy.GetMessages()
                arcpy.AddMessage(arcpy.GetMessages())
            # define calculation expression
            propCalc = "!" + eField + "! * !" + field + "!"
            # perform calculation
            try:
                arcpy.CalculateField_management(estimatesTable,newField,propCalc,"PYTHON_9.3")
                arcpy.AddMessage("calculated " + newField)
                print "Calculated " + newField
            except:
                print arcpy.GetMessages()
                arcpy.AddMessage(arcpy.GetMessages())
    ##        # delete proportion field
    ##        try:
    ##            arcpy.DeleteField_management(estimatesTable,field)
    ##        except:
    ##            arcpy.GetMessages()
arcpy.AddMessage("completed calculations")
print "Completed GR estimates in " + str(datetime.datetime.now()-processTime)
###########START UN ADJUSTMENT
processTime = datetime.datetime.now()
# select appropriate row
try:
    unTable = inputTable.replace(os.path.basename(inputTable),iso + "_un_adjustment")
    arcpy.TableSelect_analysis(inUNTable,unTable,'"ISO" = ' + "'" + iso.upper() + "'")
    arcpy.AddMessage("Created " + unTable)
    print "Created " + unTable
except:
    print arcpy.GetMessages()
    arcpy.AddMessage(arcpy.GetMessages())
    
# create list of total pop fields to summarize
summaryFields = ["E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020"]
# create empty list of adjFields to add adjField values to
adjFields = []
# iterate and summarize
for summaryField in summaryFields:
    # define outTable
    outTable = "in_memory" + os.sep + iso + "_" + summaryField #
    # summarize the field
    try:
        arcpy.Frequency_analysis(estimatesTable,outTable,"UCID0",summaryField)
        arcpy.AddMessage("Created " + outTable)
        print "Created " + outTable
    except:
        print arcpy.GetMessages()
        arcpy.AddMessage(arcpy.GetMessages())
    # join the summarized GPWPOP to the un adjustment table
    try:
        arcpy.JoinField_management(unTable,"UCID0",outTable,"UCID0",summaryField)
        arcpy.AddMessage("Joined Fields")
        print "Joined UN Fields"
    except:
        print arcpy.GetMessages()
        arcpy.AddMessage(arcpy.GetMessages())
    # add adjustment factor field
    adjField = "UNADJFAC_" + summaryField[-4:]
    numerator = "UNPOP" + summaryField[-4:]
    adjFields.append(adjField)
    try:
        arcpy.AddField_management(unTable,adjField,"DOUBLE")
    except:
        print arcpy.GetMessages()
        arcpy.AddMessage(arcpy.GetMessages())
    # calculation adjustment factor field
    calcExpression = "(!" + numerator + "!/!" + summaryField + "!) - 1" 
    try:
        arcpy.CalculateField_management(unTable,adjField,calcExpression,"PYTHON_9.3")
        arcpy.AddMessage("Calculated " + adjField)
        print "Calculated " + adjField
    except:
        print arcpy.GetMessages()
        arcpy.AddMessage(arcpy.GetMessages())
# join adjustment factor fields to the estimatesTable
try:
    arcpy.JoinField_management(estimatesTable,"UCID0",unTable,"UCID0",adjFields)
    arcpy.AddMessage("Joined Fields")
    print "Joined adjustment factors"
except:
    print arcpy.GetMessages()
    arcpy.AddMessage(arcpy.GetMessages())
# iterate through adjFields
for adjField in adjFields:    
    year = adjField[-4:]
    # Create list of fields to adjust
    eFields = arcpy.ListFields(estimatesTable,"E_*" + year)
    newFieldPrefix = "UN"         
    # iterate the eFields
    for eField in eFields:
        fieldName = eField.name
        # define newField
        newField = newFieldPrefix + fieldName
        # add newField to table
        try:            
            arcpy.AddField_management(estimatesTable,newField,"DOUBLE")
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
        # construct unAdjustment
        unAdjustment = "(!" + adjField + "! * !" + fieldName + "!) + !" + fieldName + "!"
        # perform calculation
        try:
            arcpy.CalculateField_management(estimatesTable,newField,unAdjustment,"PYTHON_9.3")
            arcpy.AddMessage("Calculated " + newField)
            print "Calculated " + newField
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
print "Completed un Adjustments in " + str(datetime.datetime.now()-processTime)      
scriptTime = datetime.datetime.now() - startTime
arcpy.AddMessage("The script completed in: " + str(scriptTime))
print "The script completed in: " + str(scriptTime)


