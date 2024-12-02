import arcpy, os, sys

arcpy.env.workspace = r'Q:\gpw\stage\fishnets'
arcpy.env.overwriteOutput = True
workspaces = arcpy.ListWorkspaces("can","Folder")
for workspace in workspaces:
    print workspace
    iso = os.path.basename(workspace)
##    inputFC = workspace + os.sep + iso +".gdb" + os.sep + iso + "_gridding"
##    print inputFC
    arcpy.env.workspace = workspace + os.sep + "tiles"
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    for gdb in gdbs:
        arcpy.env.workspace = gdb
##        tbls = arcpy.ListTables("*")
##        [arcpy.Delete_management(tbl) for tbl in tbls]
        print gdb
        fc = arcpy.ListFeatureClasses("*processed")[0]
        arcpy.Delete_management(fc)
        tbl = arcpy.ListTables("*table")[0]
        arcpy.Delete_management(tbl)
##        ol=gdb[:-4]+"lyr"
##        where ="ADMINAREAKMMASKED <0"
##        if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(fc,ol,where))[0])>0:
##            arcpy.CalculateField_management(ol,"ADMINAREAKMMASKED",0,"PYTHON")
##            arcpy.CalculateField_management(ol,"ADMINWATERAREAKM","!ADMINAREAKM!","PYTHON")
##            arcpy.CalculateField_management(ol,"AREAKMMASKED",0,"PYTHON")
##            arcpy.CalculateField_management(ol,"WATERAREAKM","!AREAKM!","PYTHON")
        
    
    
