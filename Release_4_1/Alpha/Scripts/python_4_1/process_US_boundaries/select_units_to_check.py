import arcpy, os

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\units_to_check.gdb'
hydros = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\hydrography.gdb'
tables = r'\\Dataserver0\gpw\GPW4\Release_Prelim2\Preprocessing\Country\USA\Ingest\Census\Ingest_files.gdb'

arcpy.env.overwriteOutput = True
arcpy.env.workspace = inGDB

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList[1:]:
    print fc[:6]
    arcpy.AddField_management(fc,"ATOTPOPBT","LONG")
    hydro = os.path.join(hydros,fc[:6]+"_hydrography")

    arcpy.MakeFeatureLayer_management(fc,"lyr")
    total = int(arcpy.GetCount_management('lyr').getOutput(0))
    arcpy.MakeFeatureLayer_management(hydro,"hydro")

    arcpy.SelectLayerByLocation_management("lyr","COMPLETELY_WITHIN","hydro")
    count = int(arcpy.GetCount_management('lyr').getOutput(0))

    print "Total: " + str(total)
    print "Inside: " + str(count)

    table = os.path.join(tables,fc[4:6].upper()+"_admin4_census_2010")

    ubids = {}
    with arcpy.da.SearchCursor(table,["USCID","ATOTPOPBT"]) as cursor:
        for row in cursor:
            ubids[row[0]] = row[1]

    with arcpy.da.UpdateCursor(fc,["USCID","ATOTPOPBT"]) as cursor:
        for row in cursor:
            if row[0] in ubids:
                row[1] = ubids[row[0]]
            else:
                print row[0]
            cursor.updateRow(row)

