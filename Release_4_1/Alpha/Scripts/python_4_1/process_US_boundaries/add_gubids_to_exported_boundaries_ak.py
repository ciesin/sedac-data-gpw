# Import Libraries
import arcpy, os
from arcpy import env

# Define Workspace Variable
workspace = r'Database Connections\sde.sde'
env.workspace = workspace

fds = arcpy.ListDatasets("*USA_AK*","Feature")
fds.sort()

outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\tiled_countries\usa.gdb'

fd = fds[0]
iso = fd[4:]
print iso

fdPath = os.path.join(workspace,fd)

env.workspace = fdPath
boundList = arcpy.ListFeatureClasses("*boundaries_2010")
fc = boundList[0]

ubids = {}
with arcpy.da.SearchCursor(fc,["UBID","GLOBALID"]) as cursor:
    for row in cursor:
        ubids[row[0]] = row[1]

env.workspace = outGDB
outFCList = arcpy.ListFeatureClasses("usa_ak*")
outFCList.sort()

for outFC in outFCList:
    print outFC
    with arcpy.da.UpdateCursor(outFC,["UBID","GUBID"]) as cursor:
        for row in cursor:
            if row[0] in ubids:
                row[1] = ubids[row[0]]
            else:
                print row[0] + " not in SDE"
            cursor.updateRow(row)

print "Done"
