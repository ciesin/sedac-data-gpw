#Jane Mills
#3/23/2017
#Add the data context to the gridding boundaries

# Import Libraries
import arcpy, os, csv

processFolder = r'D:\gpw\release_4_1\process'

arcpy.env.workspace = processFolder
gdbList = arcpy.ListWorkspaces("*","FILEGDB")

for gdb in gdbList:
    arcpy.env.workspace = gdb
    print gdb

    fcList = arcpy.ListFeatureClasses()
    gridFC = filter(lambda x: x[-8:]=='gridding' or x[-7:]=='context', fcList)
    if len(gridFC)> 0:
        for fc in gridFC:
            fList = arcpy.ListFields(fc,"CONTEXT")
            if len(fList) > 0:
                arcpy.DeleteField_management(fc,"CONTEXT")

print 'done'
