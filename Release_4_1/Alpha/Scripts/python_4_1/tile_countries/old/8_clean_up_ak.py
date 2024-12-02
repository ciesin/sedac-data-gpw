import arcpy, os

outFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process\tiles\usaak'

arcpy.env.workspace = outFolder

gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

for gdb in gdbs[:-3]:
    iso = os.path.basename(gdb)[:-4]
    print iso

    arcpy.env.workspace = gdb
    
    tableList = arcpy.ListTables("usaak*")
    for table in tableList:
        tileField = arcpy.ListFields(table,"tile")
        if len(tileField) == 1:
            arcpy.DeleteField_management(table,"tile")

        isoField = arcpy.ListFields(table,"ISO")
        if len(isoField) == 1:
            arcpy.CalculateField_management(table,"ISO",'"'+iso.upper()+'"',"PYTHON")

        #arcpy.Rename_management(table,"usaak"+table[8:])
