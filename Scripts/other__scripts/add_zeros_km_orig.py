# Erin Doxsey-Whitfield
# Add zeros to GPW data

# Import libraries
import arcpy
from arcpy import env

# define directories
workspace = r"D:\GPW\BRA_2010_DF_ES.gdb"

# define env.workspace
env.workspace = workspace

print env.workspace + " is the workspace"

# Create list of tables
tables=arcpy.ListTables("BRA_2010_DF_ES_men_total")

# Iterate the list
for table in tables:
    print table
    # Create list of fields
    fields=arcpy.ListFields(table,"UCID*")
    #Add new fields
    newFields=["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UTCID5","UCADMIN0","UCADMIN1","UCADMIN2","UCADMIN3","UCADMIN4","UCADMIN5"]
    for newField in newFields:
        # Create condition to check if field already exists, if it does move on, if not add it
        fieldExistList = arcpy.ListFields(table, newField)
        if len(fieldExistList) == 1:
            print newField + " already exists in " + table
        else:            
            try:
                arcpy.AddField_management(table,newField,"STRING")
                print "Added " + newField
            except:
                print arcpy.GetMessages()
            
   
    # Iterate the list of fields
    for field in fields:
        print field.name
        #Create condition to define the correct number of characters
        if field.name=="UCID0":
            fieldLength=3
            newField = "UTCID0"
            calculationField = "UCADMIN0"
            calculationExpression = "[UTCID0]"
        elif field.name=="UCID1":
            fieldLength=5
            newField = "UTCID1"
            calculationField = "UCADMIN1"
            calculationExpression = "[UTCID0] & [UTCID1]"
        elif field.name=="UCID2":
            fieldLength=7
            newField = "UTCID2"
            calculationField = "UCADMIN2"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]"
        elif field.name=="UCID3":
            fieldLength=8
            newField = "UTCID3"
            calculationField = "UCADMIN3"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3]"
        elif field.name=="UCID4":
            fieldLength=10
            newField = "UTCID4"
            calculationField = "UCADMIN4"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]"
        elif field.name=="UCID5":
            fieldLength=7
            newField = "UTCID5"
            calculationField = "UCADMIN5"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]& [UTCID5]"
        elif field.name=="UCID6":
            fieldLength=6
            newField = "UTCID6"
            calculationField = "UCADMIN6"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]& [UTCID5] &[UTCID6]"
        else:
            print "It's not any of those fields"
        print "Field length = " + str(fieldLength)
        
        # Create search cursor
        search=arcpy.UpdateCursor(table)
        for row in search:
            value=row.getValue(field.name)
            stringValue=str(int(value))
            print stringValue
            # Create condition to test length of values in row
            if len(stringValue)==fieldLength:
                extraDigits=0
                newValue=stringValue
                print "field length matches max"
            else:
                extraDigits=fieldLength-len(stringValue)
                print "Add " + str(extraDigits)+ " zeros to start of row to make the total length " + str(fieldLength)
            # Append zeroes to front of value
            while extraDigits>0:
                newValue="0"+stringValue
                stringValue=newValue
                extraDigits=extraDigits-1
            print newValue + " is the new value"
            row.setValue(newField,newValue)
            search.updateRow(row)

        # Calculate hierarchical ids
        try:
            arcpy.CalculateField_management(table,calculationField,calculationExpression,"VB","#")
            print "Calculated " + calculationField
        except:
            print arcpy.GetMessages()
        
