# Jane Mills
# 2/9/2021
# GPW
# check growth rate ID

import arcpy, os
arcpy.env.overwriteOutput = True

inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\adjusted_boundaries_with_census_data'

boundaryGDBs = [os.path.join(inFolder,b) for b in os.listdir(inFolder) if b[-4:] == '.gdb' and 'usa' not in b]
boundaryGDBs.sort()

boundaryGDB = boundaryGDBs[0]
for boundaryGDB in boundaryGDBs:
    iso = os.path.basename(boundaryGDB)[:-4]
    print(iso)
    
    arcpy.env.workspace = boundaryGDB
    
#    grBoundary = arcpy.ListFeatureClasses("*growth_rate*")
#    if len(grBoundary) == 0:
#        print("  No growth rate found")
#        continue
#    grBoundary = grBoundary[0]
    
    censusBoundary = arcpy.ListFeatureClasses(iso+"_admin*")
    censusBoundary.sort()
    censusBoundary = censusBoundary[-1]
    
    # check for nulls
    f = arcpy.ListFields(censusBoundary,'GRID')
    if len(f) == 0:
        print("  Did not find GRID")
        continue
    
    count = 0
    with arcpy.da.SearchCursor(censusBoundary,'GRID','GRID IS NULL') as cursor:
        for row in cursor:
            count += 1
    
    if count > 0:
        print("  {} rows did not get a growth rate ID".format(count))

