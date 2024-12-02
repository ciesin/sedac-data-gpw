#Jane Mills
#3/23/2017
#Calculate the coordinate fields

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
bounds = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'

arcpy.env.workspace = bounds
fcs = arcpy.ListFeatureClasses()
fcs.sort()

for fc in fcs:
    if fc[:3] == 'usa':
        iso = fc[:5]
    else:
        iso = fc[:3]
    outFC = os.path.join(centroids,iso+"_centroids")

    print iso
    coordsDict = {}

    inMemBounds = 'in_memory' + os.sep + iso
    arcpy.CopyFeatures_management(fc,inMemBounds)
    arcpy.AddGeometryAttributes_management(inMemBounds,"CENTROID")
    arcpy.AddGeometryAttributes_management(inMemBounds,"CENTROID_INSIDE")

    with arcpy.da.SearchCursor(inMemBounds,['GUBID','CENTROID_X','CENTROID_Y','INSIDE_X','INSIDE_Y']) as cursor:
        for row in cursor:
            coordsDict[row[0]] = row[1:]

    del inMemBounds

    with arcpy.da.UpdateCursor(outFC,['GUBID','CENTROID_X','CENTROID_Y','INSIDE_X','INSIDE_Y']) as rows:
        for row in rows:
            coords = coordsDict[row[0]]
            row[1] = coords[0]
            row[2] = coords[1]
            row[3] = coords[2]
            row[4] = coords[3]
            rows.updateRow(row)

    del coordsDict

print 'done'


