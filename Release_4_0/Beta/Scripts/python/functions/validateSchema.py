# Kytt MacManus
# 5-13-15
# Library of Useful Functions for GPW Validation

# import libraries
import arcpy, os, datetime, csv

# define function to check if a field exists in a feature class
def checkForField(inTable,field):
    flds = arcpy.ListFields(inTable,field)
    if len(flds)==1:
        return 1
    else:
        return 0

# define function to check if a field exists in a feature class
def checkFieldType(inTable,field,fieldType):
    fld = arcpy.ListFields(inTable,field)[0]
    if fld.type==fieldType:
        return 1
    else:
        return 0
    
# define function to check for duplicate field values
def checkForDuplicates(inTable,field,inView):
    # summarize by field
    summaryTbl = 'in_memory' + os.sep + os.path.basename(inTable) + "_summary_"  + field
    arcpy.Frequency_analysis(inTable,summaryTbl,field)
    # create table view for FREQUENCY > 1
    tblExp = "FREQUENCY > 1"
    if int(arcpy.GetCount_management(arcpy.MakeTableView_management(summaryTbl,inView,tblExp))[0])>0:
        # then there are duplicates
        return 1
    else:
        # otherwise there are no duplicates
        return 0          

# define function to validate schema
# return tuple with indication of validation and metadata
def validateSchema(inTable, inSchema):
    validationResults = []
    schemaFields = arcpy.ListFields(inSchema,"*")
    for schemaField in schemaFields:
        # check if the field exists
        if checkForField(inTable,schemaField.name)==1:
            # if field does exist then check if it matches the schemaFieldType
            if checkFieldType(inTable,schemaField.name,schemaField.type)==1:
                # if fieldtype condition is met then the field validates
                # parse results
                validationDescription = "Validates Name and Type"
                validationResult = (1,schemaField.name,schemaField.type,validationDescription)
                validationResults.append(validationResult)
            else:
                # if fieldtype condition fails then the field does not validate
                # parse results
                validationDescription = "Type Fails"
                validationResult = (2,schemaField.name,schemaField.type,validationDescription)
                validationResults.append(validationResult)
        else:
            # if field does not exist then validation fails
            # parse results
            validationDescription = "Field Missing or Named Incorrectly"
            validationResult = (3,schemaField.name,schemaField.type,validationDescription)
            validationResults.append(validationResult)
    return validationResults

# define function to check whether a condition exists in an
# attribute of a given field
def checkTableCondition(inTable,condition,yesView,yesOut,oppositeCondition,noView,noOut):  
    # create the view and check if it has any rows
    if int(arcpy.GetCount_management(arcpy.MakeTableView_management(inTable,yesView,condition))[0]) > 0:
        # if the result has rows, then export it 
        arcpy.CopyRows_management(yesView,yesOut)
        # as well as the oppositeCondition  
        if int(arcpy.GetCount_management(arcpy.MakeTableView_management(inTable,noView,oppositeCondition))[0])==0:
            # if there are no rows with oppositeCondition then sys.exit()
            conditionResults = (0, "The field is present, but no rows meet the condition: " + oppositeCondition)
            return conditionResults
        else:
            # otherwise write the rows to a new table
            arcpy.CopyRows_management(noView,noOut)
            conditionResults = (1, "Created " + yesOut + " and " + noOut)
            return conditionResults
                
    else:
        conditionResults = (0, "The field is present, but no rows meet the condition: " + condition)
        return conditionResults

# define function to validate join
def validateJoin(baseFeature,joinField,joinFeature,joinFeatureField):
    # get basecount
    baseCount = int(arcpy.GetCount_management(baseFeature)[0])
    # both tables must be views
    layer1 = os.path.basename(baseFeature) + "_lyr"
    layer2 = os.path.basename(joinFeature) + "_lyr"
    if arcpy.Exists(layer1):
        arcpy.Delete_management(layer1)
    if arcpy.Exists(layer2):
        arcpy.Delete_management(layer2)               
    try:
        arcpy.MakeFeatureLayer_management(baseFeature,layer1)
    except:
        arcpy.MakeTableView_management(baseFeature,layer1)  
    try:
        arcpy.MakeFeatureLayer_management(joinFeature,layer2)
    except:
        arcpy.MakeTableView_management(joinFeature,layer2)         
    # add a join keeping common fields
    try:
        # get join count
        joinCount = int(arcpy.GetCount_management(
            arcpy.AddJoin_management(layer1,joinField,
                                     layer2,joinFeatureField,"KEEP_COMMON"))[0])
    except:
        arcpy.GetMessages()
    # if the joinCount is less than baseCount the join does not validate
    if baseCount > joinCount:
        return 0
    else:
        return 1

# define function to stripWhiteSpace
def stripWhiteSpace(inFile):
    # list fields
    fields = arcpy.ListFields(inFile,"*")
    for field in fields:
        if field.type == "String":
            calc = '!' + field.name + '!.strip()'
            arcpy.CalculateField_management(inFile,field.name,calc,"PYTHON")
        
