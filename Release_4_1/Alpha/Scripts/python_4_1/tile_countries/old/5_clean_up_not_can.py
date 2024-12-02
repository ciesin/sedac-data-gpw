import arcpy, os

outFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process\tiles'

isos = os.listdir(outFolder)
isos.sort()

for iso in isos[1:]:
    print iso

    arcpy.env.workspace = os.path.join(outFolder,iso)

    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    gdbs.sort()

    for gdb in gdbs:
        print os.path.basename(gdb)

        arcpy.env.workspace = gdb

        fc = arcpy.ListFeatureClasses("*boundaries_2010*")[0]
        arcpy.DeleteField_management(fc,"tile")

        table = arcpy.ListTables()[0]
        arcpy.DeleteField_management(table,"tile")

