#Jane Mills
#2/28/2017
#All of the GUBIDS have been calculated as version SDE, but do not show up when you're in an edit version
#They also haven't been calculated for USA (MO, NJ:)

# Import Libraries
import arcpy, os
from arcpy import env

# Define Workspace Variable
workspace = r'Database Connections\GPW4.sde'
env.workspace = workspace

fds = arcpy.ListDatasets("*","Feature")
fds.sort()

# iterate
#fd = fds[0]

for fd in fds:
    iso = fd[4:]
    print iso

    fdPath = os.path.join(workspace,fd)

    env.workspace = fdPath
    boundList = arcpy.ListFeatureClasses("*boundaries_2010")
    fc = boundList[0]

    #Create layer file, change version, start editing, calculate gubid?
    arcpy.MakeFeatureLayer_management(fc, "layer")
    arcpy.ChangeVersion_management("layer","TRANSACTIONAL","GPW4.GPW_4_1_alpha_edits")

    edit = arcpy.da.Editor(workspace)
    edit.startEditing(False, True)
    edit.startOperation()

    with arcpy.da.UpdateCursor(fc,['GUBID','GLOBALID']) as cursor:
        for row in cursor:
            row[0] = row[1]
            cursor.updateRow(row)

    edit.stopOperation()
    edit.stopEditing(True)

print "Done"
