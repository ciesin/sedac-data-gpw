import arcpy, os, sys

arcpy.env.workspace = r'Q:\gpw\stage\pop_tables'
arcpy.env.overwriteOutput = True
workspaces = arcpy.ListWorkspaces("can","Folder")
for workspace in workspaces:
    print workspace
    iso = os.path.basename(workspace)
    inputFC = workspace + os.sep + iso +".gdb" + os.sep + iso + "_gridding"
    print inputFC
    arcpy.env.workspace = workspace + os.sep + "tiles"
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    for gdb in gdbs:
        arcpy.env.workspace = gdb
##        tbls = arcpy.ListTables("*")
##        [arcpy.Delete_management(tbl) for tbl in tbls]
##
        fc = arcpy.ListFeatureClasses("*beta")[0]
        outFile = gdb + os.sep + os.path.basename(gdb)[:-4] + "_gridding"
        arcpy.Clip_analysis(inputFC,fc,outFile)
##        arcpy.Rename_management(fc, fc +"_beta")
        print "created " + outFile
        
    
    
