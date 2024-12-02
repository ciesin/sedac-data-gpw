import arcpy, os
arcpy.env.workspace = r'D:\GPW\jrc\jrc_data.gdb'
outGDB = r'D:\GPW\jrc\aggregated_data.gdb'
doNotShare = ["ARE","AUT","BHR","BLZ","CHN",
              "CYP","HKG","HUN","IND","ISR",
              "JEY","KAZ","KEN","KHM","LKA",
              "LVA","MAC","MDG","MEX","MLT",
              "MWI","MYS","MYT","NCL","NFK",
              "NLD","OMN","POL","PRT","PSE",
              "PYF","ROU","SGP","SVK","TCD",
              "UZB"]

for iso in doNotShare:
    fc = arcpy.ListFeatureClasses(iso + "*")[0]
    print fc
    adminLevel = str(fc).split("_")[1]
    if adminLevel == "admin1":
        disField = "NAME0"
        level = "_admin0"
    else:
        disField = "NAME1"
        level = "_admin1"
    outFC = outGDB + os.sep + str(fc).split("_")[0] + level + "_dissolve"
    dissolveStats = [["UNE_ATOTPOPBT_1975","SUM"],
                     ["UNE_ATOTPOPBT_1990","SUM"],
                     ["UNE_ATOTPOPBT_2000","SUM"],
                     ["UNE_ATOTPOPBT_2015","SUM"]]
    arcpy.Dissolve_management(fc,outFC,disField,dissolveStats)
    print "Created " + outFC
    fldList = ["UNE_ATOTPOPBT_1975","UNE_ATOTPOPBT_1990",
               "UNE_ATOTPOPBT_2000","UNE_ATOTPOPBT_2015"]
    for fld in fldList:
        sumField = "SUM_" + fld
        arcpy.AddField_management(outFC,fld,"LONG")
        arcpy.CalculateField_management(outFC,fld,"!"+sumField+"!","PYTHON")
        arcpy.DeleteField_management(outFC,sumField)
    print "Updated attributes"
