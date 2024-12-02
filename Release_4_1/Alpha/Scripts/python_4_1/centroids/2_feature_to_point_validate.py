#Jane Mills
#3/23/2017
#Make sure all features are present in the centroids

# Import Libraries
import arcpy, os

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

    origCount = 0
    cenCount = 0

    with arcpy.da.SearchCursor(fc,"GUBID") as rows:
        for row in rows:
            origCount += 1

    cen = os.path.join(outGDB,iso+"_centroids")
    with arcpy.da.SearchCursor(cen,"GUBID") as rows:
        for row in rows:
            cenCount += 1

    if not origCount == cenCount:
        print "different number of features"

print 'done'


