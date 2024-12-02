import arcpy, os
from arcpy import env

sde = r'Database Connections\sde.sde'

env.workspace = sde

fdList = arcpy.ListDatasets("*USA_*")
fdList.sort()

for fd in fdList:
    print fd
    fdPath = os.path.join(sde, fd)

    arcpy.RegisterAsVersioned_management(fdPath)
    arcpy.EnableArchiving_management(fdPath)
    
    print "registered, enabled"

print "done"
