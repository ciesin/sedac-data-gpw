# Import Libraries
import arcpy, os
from arcpy import env

# Define Workspace Variable
workspace = r'Database Connections\sde.sde'
env.workspace = workspace

fds = arcpy.ListDatasets("*USA_MO*","Feature")

for fd in fds:
    iso = fd[4:]
    print iso

    fdPath = os.path.join(workspace,fd)
    #arcpy.AddGlobalIDs_management(fdPath)

    env.workspace = fdPath
    boundList = arcpy.ListFeatureClasses("*boundaries_2010")
    fc = boundList[0]

    arcpy.CalculateField_management(fc,"GUBID","!GLOBALID!","PYTHON")

print "Done"
