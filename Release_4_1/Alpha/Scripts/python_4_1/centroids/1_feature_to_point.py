#Jane Mills
#3/23/2017
#Convert polygon to raster and load to the centroid template

# Import Libraries
import arcpy, os

template = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\template.gdb\template'
inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'

arcpy.env.workspace = inGDB
arcpy.env.overwriteOutput = True

fcs = arcpy.ListFeatureClasses()
fcs.sort()

# Iterate through fcs
for fc in fcs:

    iso = fc[:3]
    print iso  
    
    # Convert polygon to point
    inMemCentroids = 'in_memory' + os.sep + iso
    arcpy.FeatureToPoint_management(fc,inMemCentroids,"CENTROID")

    outFC = os.path.join(outGDB,iso+"_centroids")
    arcpy.CopyFeatures_management(template,outFC)
    arcpy.Append_management(inMemCentroids,outFC,"NO_TEST")

    del inMemCentroids

print 'done'


