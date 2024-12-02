#Jane Mills
#5/18/2017
#Add UCADMIN codes to gridding boundaries

# Import Libraries
import arcpy, os

gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1_updated.gdb'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1_final.gdb'
template = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\ancillary.gdb\gridding_boundary_template'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    iso = fc[:-23]
    print iso
    outFC = os.path.join(outGDB,fc)
    arcpy.CopyFeatures_management(template,outFC)
    arcpy.Append_management(fc,outFC,"NO_TEST")

print 'done'


