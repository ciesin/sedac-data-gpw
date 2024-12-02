import arcpy,os,csv
arcpy.env.workspace = r'D:\gpw\release_4_1\loading\processed'
gdbs=arcpy.ListWorkspaces("*","FILEGDB")

for gdb in gdbs:
    arcpy.env.workspace = gdb
    tbl = arcpy.ListTables("*estimates")[0]
    tblView = tbl + "view"
    arcpy.MakeTableView_management(tbl, tblView,"ATOTPOPBT <0")
    if int(arcpy.GetCount_management(tblView)[0])>0:
        outFile = r'D:\gpw\release_4_1\loading\scratch\negatives.gdb' + os.sep + tbl
        arcpy.CopyRows_management(tblView,outFile)
        print "Created " + outFile
