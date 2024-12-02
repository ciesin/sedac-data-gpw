# Erin Doxsey-Whitfield
# Add zeros to GPW data

# Import libraries
import arcpy
from arcpy import env

# define directories
workspace = arcpy.GetParameterAsText(0)
##workspace = r"\\Dataserver0\gpw\GPW4\Gridding\country\inputs\jpn.gdb"

# define env.workspace
env.workspace = workspace

print env.workspace + " is the workspace"

# Create list of tables
censusTable=arcpy.GetParameterAsText(1)
censusAdminLevel=arcpy.GetParameterAsText(2)
##censusTable=r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\jpn.gdb\JPN_admin2_census_2010'
##censusAdminLevel = 2

# Create list of fields
fields=arcpy.ListFields(censusTable,"UCADMIN*")

#Add new fields
if censusAdminLevel == "0":
    newFields = ["UTCID0", "UCID0"]
elif censusAdminLevel == "1":
    newFields =["UTCID0","UTCID1","UCID0","UCID1"]
elif censusAdminLevel == "2":
    newFields =["UTCID0","UTCID1","UTCID2","UCID0","UCID1","UCID2"]
elif censusAdminLevel == "3":
    newFields =["UTCID0","UTCID1","UTCID2","UTCID3","UCID0","UCID1","UCID2","UCID3"]
elif censusAdminLevel == "4":
    newFields =["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UCID0","UCID1","UCID2","UCID3","UCID4"]
elif censusAdminLevel == "5":
    newFields =["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UTCID5","UCID0","UCID1","UCID2","UCID3","UCID4","UCID5"]
elif censusAdminLevel == "6":
    newFields =["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UTCID5","UTCID6","UCID0","UCID1","UCID2","UCID3","UCID4","UCID5","UCID6"]
else:
    pass

for newField in newFields:
    # Create condition to check if field already exists, if it does move on, if not add it
    fieldExistList = arcpy.ListFields(censusTable, newField)
    if len(fieldExistList) == 1:
        print newField + " already exists in " +censusTable
        arcpy.AddMessage(newField + " already exists in " +censusTable)
    else:            
        try:
            arcpy.AddField_management(censusTable,newField,"STRING")
            print "Added " + newField
            arcpy.AddMessage("Added " + newField)
        except:
            print arcpy.GetMessages()
        

# Iterate the list of fields
for field in fields:
    print field.name
    arcpy.AddMessage(field.name)
    
    #Create condition to define the correct number of characters
    if field.name=="UCADMIN0":
        fieldLength=3
        newField = "UTCID0"
        calculationField = "UCID0"
        calculationExpression = "[UTCID0]"
    elif field.name=="UCADMIN1":
        fieldLength=5
        newField = "UTCID1"
        calculationField = "UCID1"
        calculationExpression = "[UTCID0] & [UTCID1]"
    elif field.name=="UCADMIN2":
        fieldLength=7
        newField = "UTCID2"
        calculationField = "UCID2"
        calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]"
    elif field.name=="UCADMIN3":
        fieldLength=8
        newField = "UTCID3"
        calculationField = "UCID3"
        calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3]"
    elif field.name=="UCADMIN4":
        fieldLength=10
        newField = "UTCID4"
        calculationField = "UCID4"
        calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]"
    elif field.name=="UCADMIN5":
        fieldLength=7
        newField = "UTCID5"
        calculationField = "UCID5"
        calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]& [UTCID5]"
    elif field.name=="UCADMIN6":
        fieldLength=6
        newField = "UTCID6"
        calculationField = "UCID6"
        calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]& [UTCID5] &[UTCID6]"
    else:
        print "It's not any of those fields"
        arcpy.GetMessages("It's not any of those fields")
        arcpy.GetMessages("It's not any of those fields")
    print "Field length = " + str(fieldLength)
    arcpy.AddMessage("Field length = " + str(fieldLength))
    
    # Create search cursor
    search=arcpy.UpdateCursor(censusTable)
    for row in search:
        value=row.getValue(field.name)
        stringValue=str(int(value))
        print stringValue
        arcpy.AddMessage(stringValue)
        # Create condition to test length of values in row
        if len(stringValue)==fieldLength:
            extraDigits=0
            newValue=stringValue
            print "field length matches max"
            arcpy.AddMessage("field length matches max")
        else:
            extraDigits=fieldLength-len(stringValue)
            print "Add " + str(extraDigits)+ " zeros to start of row to make the total length " + str(fieldLength)
            arcpy.AddMessage("Add " + str(extraDigits)+ " zeros to start of row to make the total length " + str(fieldLength))
        # Append zeroes to front of value
        while extraDigits>0:
            newValue="0"+stringValue
            stringValue=newValue
            extraDigits=extraDigits-1
        print newValue + " is the new value"
        arcpy.AddMessage(newValue + " is the new value")
        row.setValue(newField,newValue)
        search.updateRow(row)

    # Calculate hierarchical ids
    try:
        arcpy.CalculateField_management(censusTable,calculationField,calculationExpression,"VB","#")
        print "Calculated " + calculationField
        arcpy.AddMessage("Calculated " + calculationField)
    except:
        print arcpy.GetMessages()
    
