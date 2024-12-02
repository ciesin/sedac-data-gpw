import arcpy, os

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\2_inland_boundaries.gdb'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\units_to_check.gdb'
table = os.path.join(outGDB,'units_not_in_v40_boundaries')

arcpy.env.overwriteOutput = True

stateList = []
ubids = {}
with arcpy.da.SearchCursor(table,["State","UBID"]) as cursor:
    for row in cursor:
        ubids[row[1]] = 1
        if not row[0] in stateList:
            stateList.append(row[0])
        

for state in stateList:
    print state

    fc = os.path.join(inGDB,state+"_inland")
    arcpy.AddField_management(fc,"check","SHORT")
    with arcpy.da.UpdateCursor(fc,["UBID","check"]) as cursor:
        for row in cursor:
            if row[0] in ubids:
                row[1] = 1
            cursor.updateRow(row)

    arcpy.FeatureClassToFeatureClass_conversion(fc,outGDB,state+"_units_to_check","check = 1")

    arcpy.DeleteField_management(fc,"check")


