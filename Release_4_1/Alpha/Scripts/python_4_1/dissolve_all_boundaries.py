import arcpy, os
from arcpy import env

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\from_sde\country_boundaries_hi_res.gdb'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\from_sde\country_boundaries_hi_res_dissolve.gdb'

env.workspace = inGDB

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    iso = fc[:3]
    print iso

##    with arcpy.da.UpdateCursor(fc,["ISO","UBID"]) as cursor:
##        for row in cursor:
##            row[0] = iso
##            cursor.updateRow(row)

    outFC = os.path.join(outGDB,iso+"_admin0")
    arcpy.Dissolve_management(fc,outFC,"ISO","","SINGLE_PART","DISSOLVE_LINES")

    print "dissolved"
