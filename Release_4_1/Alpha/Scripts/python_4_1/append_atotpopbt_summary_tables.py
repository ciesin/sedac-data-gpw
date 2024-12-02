import arcpy,os,csv
arcpy.env.workspace = r'D:\gpw\release_4_1\loading\processed'
arcpy.env.overwriteOutput = True

template = r'D:\gpw\release_4_1\loading\templates.gdb\estimates_total_pop_summary_template'
inMemTemplate = 'in_memory' + os.sep + 'estimates_summary_'
arcpy.CopyRows_management(template,inMemTemplate)
gdbs=arcpy.ListWorkspaces("*","FILEGDB")
for gdb in gdbs:
    arcpy.env.workspace = gdb
    tbl = arcpy.ListTables("*total_pop_summary")[0]
    arcpy.Append_management(tbl,inMemTemplate,"NO_TEST")
    print "Appended " + tbl

arcpy.CalculateField_management(inMemTemplate,"FIRST_ISO","!FIRST_ISO![:3]","PYTHON")

summaryTable = inMemTemplate + "_summary"
summaryFields = []
summaryParams = arcpy.ListFields(inMemTemplate,"SUM_E*")+arcpy.ListFields(inMemTemplate,"SUM_UNE*")
for summaryParam in summaryParams:
    summaryFields.append([summaryParam.name,"SUM"])
arcpy.Statistics_analysis(inMemTemplate,summaryTable,summaryFields,"FIRST_ISO")



outFile = r'D:\gpw\release_4_1\loading\loading_table.gdb\total_pop_estimates_summary_2_22_2017'
arcpy.CopyRows_management(summaryTable,outFile)
outXLS = r'D:\gpw\release_4_1\loading' + os.sep + os.path.basename(outFile)+".xls"
arcpy.TableToExcel_conversion(outFile,outXLS)


##cursor = arcpy.da.InsertCursor(outFile,"*") 
##with arcpy.da.SearchCursor(summaryTable,"*") as rows:
##    for row in rows:
##        cursor.insertRow(row)
##
##del cursor

print "Script Complete"
