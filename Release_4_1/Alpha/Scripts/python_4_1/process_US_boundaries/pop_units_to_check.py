import arcpy, os

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\units_to_check.gdb'
tables = r'\\Dataserver0\gpw\GPW4\Release_Prelim2\Preprocessing\Country\USA\Ingest\Census\Ingest_files.gdb'

arcpy.env.overwriteOutput = True
arcpy.env.workspace = inGDB

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc[:6]
    arcpy.AddField_management(fc,"ATOTPOPBT","LONG")

    table = os.path.join(tables,fc[4:6].upper()+"_admin4_census_2010")

    ubids = {}
    with arcpy.da.SearchCursor(table,["USCID","ATOTPOPBT"]) as cursor:
        for row in cursor:
            ubids[row[0]] = row[1]

    tPop = 0
    with arcpy.da.UpdateCursor(fc,["UBID","ATOTPOPBT"]) as cursor:
        for row in cursor:
            if row[0] in ubids:
                row[1] = ubids[row[0]]
                tPop += ubids[row[0]]
            else:
                print row[0]
            cursor.updateRow(row)

    print tPop

