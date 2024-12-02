#Jane Mills
#8/5/2019
#Create census boundaries with data
#CLean up gridding boundaries (delete attributes)


import arcpy

inGDB = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\adjusted_boundaries_with_census_data'

arcpy.env.workspace = inGDB
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    level = fc[-17]
    iso = fc[:3]
    
    if level != '0' and iso != 'usa':
        count = [0]*int(level)
        for i in range(1,int(level)):
            with arcpy.da.SearchCursor(fc,'NAME'+str(i),"NAME"+str(i)+" = 'NA'") as cursor:
                for row in cursor:
                    count[i-1] += 1
    
        if sum(count) > 0:
            print(iso+": Found NAs")
    
