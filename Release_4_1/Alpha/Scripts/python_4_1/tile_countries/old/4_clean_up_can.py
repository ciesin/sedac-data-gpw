import arcpy, os

outFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process\tiles\can'

arcpy.env.workspace = outFolder

gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

for gdb in gdbs:
    print os.path.basename(gdb)

    arcpy.env.workspace = gdb
    
    fcList = arcpy.ListFeatureClasses("*boundaries_2010*")
    for fc in fcList:
        arcpy.DeleteField_management(fc,"tile")

    table = arcpy.ListTables()[0]
    arcpy.DeleteField_management(table,"tile")

