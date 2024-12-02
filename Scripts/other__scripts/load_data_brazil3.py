import arcpy, os

workspace = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\BRA\Ingest\Census\working.gdb'

arcpy.env.workspace = workspace

arcpy.env.overwriteOutput = True
# Define Input File
inputFile = workspace + os.sep + "bra_2010_v4"
fieldWildCard = "A*"
nullReplacementValue = -8888

# Create List of Fields
fieldList = arcpy.ListFields(inputFile, fieldWildCard)

# Iterate List
for field in fieldList:
    fieldName = field.name
    print "Processing " + fieldName
    # Create Table View of Null Entries in Field
    selectionExpression = '"' +  fieldName + '" < 0'
    outView = "in_memory" + os.sep + "bra_" + fieldName
    try:
        arcpy.MakeTableView_management(inputFile, outView, selectionExpression)
        print "Created " + outView
    except:
        print arcpy.GetMessages()
    # Get count
    try:
        count = arcpy.GetCount_management(outView)
        print "Count = " + str(count)
    except:
        print arcpy.GetMessages()
    if count[0] > 0:
        print "There are negatives in " + fieldName
        # Calculate Field
        try:
            arcpy.CalculateField_management(outView, fieldName, nullReplacementValue, "PYTHON")
            print "Recoded Negatives in " + fieldName
        except:
            print arcpy.GetMessages()
    else:
        print fieldName + " has no negatives"
