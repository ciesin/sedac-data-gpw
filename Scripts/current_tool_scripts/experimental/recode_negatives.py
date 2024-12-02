# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv, datetime
arcpy.CheckOutExtension("SPATIAL")
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
outWorkspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
arcpy.CheckOutExtension("SPATIAL")

wildCards = ["pak","kaz","mdg","mys","tza"]#"per","ury","can",
for wildCard in wildCards:
    countryTime = datetime.datetime.now()
    gdb = workspace + os.sep + wildCard + ".gdb"
    ISO = wildCard
    arcpy.env.workspace = gdb
    fishnet = gdb + os.sep + ISO + "_fishnet"
    fields = arcpy.ListFields(fishnet,"*")
    for field in fields:
        fieldName = field.name
        if fieldName == "Shape":
            pass
        else:            
            whereClause = fieldName + " <= 0"
            fieldLYR = ISO + fieldName
            arcpy.MakeFeatureLayer_management(fishnet,fieldLYR,whereClause)
            if not arcpy.GetCount_management(fieldLYR)[0]=='0':
                startTime = datetime.datetime.now()
                arcpy.CalculateField_management(fieldLYR,fieldName,0,"PYTHON")
                print "Calculated " + fieldName
                print str(datetime.datetime.now() - startTime)
            else:
                pass
    print "Processed " + wildCard
    print str(datetime.datetime.now() - countryTime)
