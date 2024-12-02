import arcpy, os

root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\pop_tables'
#root = r'E:\GPW\scratch'

arcpy.env.workspace = root
gdbList = arcpy.ListWorkspaces("*","FILEGDB")
gdbList.sort()

for gdb in gdbList[12:]:
    print os.path.basename(gdb)
    arcpy.env.workspace = gdb

    tableList = arcpy.ListTables("*estimates*")

    if len(tableList) > 0:
        for table in tableList:
            if "total_pop" in table:
                pass
            elif 'summary' in table:
                if 'SUM_E_ATOTPOPFT_2010' in [f.name for f in arcpy.ListFields(table)]:
                    arcpy.AlterField_management(table,'SUM_E_ATOTPOPFT_2010','temp_male','temp_male')
                    
                    arcpy.AlterField_management(table,'SUM_E_ATOTPOPMT_2010','SUM_E_ATOTPOPFT_2010','SUM_E_ATOTPOPFT_2010')
                    arcpy.AlterField_management(table,'temp_male','SUM_E_ATOTPOPMT_2010','SUM_E_ATOTPOPMT_2010')
                    print "altered:", table

            else:
                if 'E_ATOTPOPFT_2010' in [f.name for f in arcpy.ListFields(table)]:
                    arcpy.AlterField_management(table,'E_ATOTPOPFT_2010','temp_male','temp_male')
                    
                    arcpy.AlterField_management(table,'E_ATOTPOPMT_2010','E_ATOTPOPFT_2010','E_ATOTPOPFT_2010')
                    arcpy.AlterField_management(table,'temp_male','E_ATOTPOPMT_2010','E_ATOTPOPMT_2010')
                    print "altered:", table

    arcpy.Compact_management(gdb)

print "done"

