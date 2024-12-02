# Kytt MacManus
# 3-19-15

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


# define function to validate schema
# return tuple with indication of validation and metadata
def validateSchema(inTable, inSchema, schemaFields, diagnosticTable, csvFile):
    for schemaField in schemaFields:
        # check if the field exists
        if checkForField(inTable,schemaField.name)==1:
            # if field does exist then check if it matches the schemaFieldType
            if checkFieldType(inTable,schemaField.name,schemaField.type)==1:
                # if fieldtype condition is met then the field validates
                # parse results
                validationDescription = "Validates Name and Type"
                validationResult = (1,schemaField.name,schemaField.type,validationDescription)
            else:
                # if fieldtype condition fails then the field does not validate
                # parse results
                validationDescription = "Type Fails"
                validationResult = (0,schemaField.name,schemaField.type,validationDescription)
        else:
            # if field does not exist then validation fails
            # parse results
            validationDescription = "Name Fails"
            validationResult = (0,schemaField.name,schemaField.type,validationDescription)
        # write result to csvFile
        csvFile.writerow((inTable[:3],validationResult[0],validationResult[1],validationResult[2],validationResult[3]))
# def main
def main():
    # set counter
    startTime = datetime.datetime.now()
    # define inSchema
    inSchema = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr.gdb\agr_merged'
    # list schemaFields
    schemaFields = arcpy.ListFields(inSchema,"*")
    # define diagnosticTable
    diagnosticTable = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\validation\agr_attributes_3_20_15.csv'
    # open csv file and write header
    csvFile = csv.writer(open(diagnosticTable,'wb'))
    csvFile.writerow(("country","field","ftype"))#(("country","valid","field","ftype","description"))
    # define working directory
    workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr_tables.gdb'
    arcpy.env.workspace = workspace
    # list tables
    tables = arcpy.ListTables("*")
    tables.sort()
    for inTable in tables:
        processTime = datetime.datetime.now()
        print "Processing " + inTable[:3]
        flds = arcpy.ListFields(inTable,"*")
        for fld in flds:
            csvFile.writerow((inTable[:3],fld.name,fld.type))
        # execute function
##        validateSchema(inTable, inSchema, schemaFields, diagnosticTable,csvFile)
        print "Completed " + inTable
        print datetime.datetime.now() - processTime
    del csvFile
    print "Completed Script"
    print datetime.datetime.now() - startTime

if __name__ == '__main__':
    main()
 
