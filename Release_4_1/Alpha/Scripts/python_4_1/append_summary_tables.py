import arcpy,os,csv
arcpy.env.workspace = r'D:\gpw\release_4_1\loading\processed'
arcpy.env.overwriteOutput = True

template = r'D:\gpw\release_4_1\loading\templates.gdb\estimates_summary_template'
inMemTemplate = 'in_memory' + os.sep + 'estimates_summary_'
arcpy.CopyRows_management(template,inMemTemplate)
gdbs=arcpy.ListWorkspaces("*","FILEGDB")
for gdb in gdbs:
    arcpy.env.workspace = gdb
    tbl = arcpy.ListTables("*summary")[0]
    arcpy.Append_management(tbl,inMemTemplate,"NO_TEST")
    print "Appended " + tbl

arcpy.CalculateField_management(inMemTemplate,"FIRST_ISO","!FIRST_ISO![:3]","PYTHON")

summaryTable = inMemTemplate + "_summary"
summaryFields = []
summaryParams = arcpy.ListFields(inMemTemplate,"SUM*")
for summaryParam in summaryParams:
    summaryFields.append([summaryParam.name,"SUM"])
arcpy.Statistics_analysis(inMemTemplate,summaryTable,summaryFields,"FIRST_ISO")

arcpy.AddField_management(summaryTable,"MFCALC","DOUBLE")
arcpy.CalculateField_management(summaryTable,"MFCALC","!SUM_SUM_E_ATOTPOPMT_2010! + !SUM_SUM_E_ATOTPOPFT_2010!","PYTHON") 
arcpy.AddField_management(summaryTable,"MFDIFF","DOUBLE")
arcpy.CalculateField_management(summaryTable,"MFDIFF","!SUM_SUM_E_ATOTPOPBT_2010! - !MFCALC!","PYTHON")

arcpy.AddField_management(summaryTable,"AGECALC","DOUBLE")
arcpy.CalculateField_management(summaryTable,"AGECALC",
                               "!SUM_SUM_E_A000_004BT_2010! + !SUM_SUM_E_A005_009BT_2010! + !SUM_SUM_E_A010_014BT_2010! + !SUM_SUM_E_A015_019BT_2010!+ !SUM_SUM_E_A020_024BT_2010! + !SUM_SUM_E_A025_029BT_2010!+ !SUM_SUM_E_A030_034BT_2010! + !SUM_SUM_E_A035_039BT_2010!+ !SUM_SUM_E_A040_044BT_2010! + !SUM_SUM_E_A045_049BT_2010!+ !SUM_SUM_E_A050_054BT_2010! + !SUM_SUM_E_A055_059BT_2010!+ !SUM_SUM_E_A060_064BT_2010! + !SUM_SUM_E_A065PLUSBT_2010!"
                                ,"PYTHON") 
arcpy.AddField_management(summaryTable,"AGEDIFF","DOUBLE")
arcpy.CalculateField_management(summaryTable,"AGEDIFF","!SUM_SUM_E_ATOTPOPBT_2010! - !AGECALC!","PYTHON")

arcpy.AddField_management(summaryTable,"MFAGECALC","DOUBLE")
arcpy.CalculateField_management(summaryTable,"MFAGECALC",
                               "!SUM_SUM_E_A000_004MT_2010! + !SUM_SUM_E_A005_009MT_2010!+ !SUM_SUM_E_A010_014MT_2010! + !SUM_SUM_E_A015_019MT_2010! + !SUM_SUM_E_A020_024MT_2010! + !SUM_SUM_E_A025_029MT_2010!+ !SUM_SUM_E_A030_034MT_2010! + !SUM_SUM_E_A035_039MT_2010!+ !SUM_SUM_E_A040_044MT_2010! + !SUM_SUM_E_A045_049MT_2010!+ !SUM_SUM_E_A050_054MT_2010! + !SUM_SUM_E_A055_059MT_2010!+ !SUM_SUM_E_A060_064MT_2010! + !SUM_SUM_E_A065PLUSMT_2010!+ !SUM_SUM_E_A000_004FT_2010! + !SUM_SUM_E_A005_009FT_2010!+ !SUM_SUM_E_A010_014FT_2010! + !SUM_SUM_E_A015_019FT_2010!+ !SUM_SUM_E_A020_024FT_2010! + !SUM_SUM_E_A025_029FT_2010!+ !SUM_SUM_E_A030_034FT_2010! + !SUM_SUM_E_A035_039FT_2010!+ !SUM_SUM_E_A040_044FT_2010! + !SUM_SUM_E_A045_049FT_2010!+ !SUM_SUM_E_A050_054FT_2010! + !SUM_SUM_E_A055_059FT_2010!+ !SUM_SUM_E_A060_064FT_2010! + !SUM_SUM_E_A065PLUSFT_2010!"
                                ,"PYTHON") 
arcpy.AddField_management(summaryTable,"MFAGEDIFF","DOUBLE")
arcpy.CalculateField_management(summaryTable,"MFAGEDIFF","!SUM_SUM_E_ATOTPOPBT_2010! - !MFAGECALC!","PYTHON")



outFile = r'D:\gpw\release_4_1\loading\loading_table.gdb\estimates_summary_2_21_2017'
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
