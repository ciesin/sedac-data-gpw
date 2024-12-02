# Import Libraries
import arcpy, os
from arcpy import env

# Define Workspace Variable
workspace = r'Database Connections\sde.sde'
env.workspace = workspace

fds = arcpy.ListDatasets("*","Feature")
fds.sort()

# iterate
for fd in fds[177:]:
    iso = fd[4:]
    if len(fd) == 7:
        print iso

        fdPath = os.path.join(workspace,fd)
        arcpy.AddGlobalIDs_management(fdPath)

        env.workspace = fdPath
        boundList = arcpy.ListFeatureClasses("*boundaries_2010")
        fc = boundList[0]

        arcpy.CalculateField_management(fc,"GUBID","!GLOBALID!","PYTHON")

    else:
        print iso + ": not doing the usa or the watermask"

print "Done"
