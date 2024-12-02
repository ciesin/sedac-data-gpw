import arcpy, os

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\tiger_projected.gdb'
arcpy.env.workspace = inGDB

water = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\usa_working.gdb\usa_water_blocks_coastal'

waterList = []
with arcpy.da.SearchCursor(water,'UBID') as cursor:
    for row in cursor:
        waterList.append(row[0])

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc

    arcpy.AddField_management(fc,"BOUNDARY_CONTEXT","SHORT")
    arcpy.AddField_management(fc,"coastal_water","SHORT")

    with arcpy.da.UpdateCursor(fc,['UBID','ALAND10','BOUNDARY_CONTEXT','coastal_water']) as cursor:
        for row in cursor:
            if row[1] == 0:
                row[2] = 7
            if row[0] in waterList:
                row[3] = 1
            elif row[0] not in waterList:
                row[3] = 0
            cursor.updateRow(row)
    

    
    

