# sorry this script is dirty and not commented, working fast

import arcpy, os, sys, imp
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')




outGDB = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\country_tables_beta.gdb'

arcpy.env.workspace = outGDB

tables = arcpy.ListTables("can*")
schemaTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb\growth_rate'

for table in tables:
    print "Processing: " + table
    validationResults = custom.validateSchema(table,schemaTable)
    # custom.validateSchema captures missing field names and incorrect field types
    for validationResult in validationResults:
        # if the validation result fails based on type
        # then transfer the data to a field of the same
        # name and type
        if validationResult[0]==2:
            print validationResult
            arcpy.AddMessage(validationResult)
            # transfer the field to new field of the same name
            # but with the correct type
            validationField = str(validationResult[1])
            validationType = str(validationResult[2])
            tmpField = validationField + "_tmp"
            tmpCalc = '!'+validationField+'!'
            validationCalc = '!'+tmpField+'!'
            try:
                arcpy.AddField_management(table,tmpField,validationType)
                arcpy.CalculateField_management(table,tmpField,tmpCalc,"PYTHON")
                arcpy.DeleteField_management(table,validationField)
                arcpy.AddField_management(table,validationField,validationType)
                arcpy.CalculateField_management(table,validationField,validationCalc,"PYTHON")
                arcpy.DeleteField_management(table,tmpField)
                print 'Corrected field type for: ' + validationField
                arcpy.AddMessage('Corrected field type for: ' + validationField)
            except:
                print arcpy.GetMessages()
        # if the validation fails based on a missing field name, then human intervention is needed
        # to decide if the field needs to be added or renamed
        elif validationResult[0]==3:
            print validationResult
            arcpy.AddMessage(validationResult)
##            validationReports.append((1,"Schema validation failure, missing field: " + validationResult[1],None))
        
