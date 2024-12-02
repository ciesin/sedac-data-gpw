import arcpy, os

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\units_to_check.gdb'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\2_inland_boundaries.gdb'

arcpy.env.overwriteOutput = True
arcpy.env.workspace = inGDB

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc[:6]

    updateFC = os.path.join(outGDB,fc[:6]+"_inland")
    
    ubids = {}
    with arcpy.da.SearchCursor(fc,["UBID","ATOTPOPBT"]) as cursor:
        for row in cursor:
            if row[1] == 0:
                ubids[row[0]] = 0

    with arcpy.da.UpdateCursor(updateFC,["UBID","BOUNDARY_CONTEXT"]) as cursor:
        for row in cursor:
            if row[0] in ubids:
                row[1] = 5
            cursor.updateRow(row)


