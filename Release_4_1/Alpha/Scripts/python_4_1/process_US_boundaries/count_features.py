import arcpy

bounds = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'
arcpy.env.workspace = bounds

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc
    water = 0
    total = 0
    with arcpy.da.SearchCursor(fc,["UBID","BOUNDARY_CONTEXT"]) as cursor:
        for row in cursor:
            if row[1] == 7:
                water += 1
            else:
                total += 1
    print total
    print water

usa = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\tiled_countries\usa.gdb'
arcpy.env.workspace = usa
fcList = arcpy.ListFeatureClasses()
fcList.sort()

print "usa"
total = 0
water = 0
for fc in fcList:
    with arcpy.da.SearchCursor(fc,["UBID","BOUNDARY_CONTEXT"]) as cursor:
        for row in cursor:
            if row[1] == 7:
                water += 1
            else:
                total += 1
print total
print water

