# Jane Mills
# 2/9/2021
# GPW
# Add growth rate ID to growth rate boundaries and high level census data

import arcpy, os
arcpy.env.overwriteOutput = True

inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\adjusted_boundaries_with_census_data'
#scratchGDB = r'D:\ESRI_home\scratch.gdb'
scratchGDB = r'F:\GPW_scratch\scratch.gdb'

boundaryGDBs = [os.path.join(inFolder,b) for b in os.listdir(inFolder) if b[-4:] == '.gdb']
boundaryGDBs.sort()

boundaryGDB = boundaryGDBs[42]
for boundaryGDB in boundaryGDBs:
    iso = os.path.basename(boundaryGDB)[:-4]
    print(iso)
    
    arcpy.env.workspace = boundaryGDB
    grBoundary = arcpy.ListFeatureClasses("*growth_rate*")
    if len(grBoundary) == 0:
        print("  No growth rate found")
        continue
    
    grBoundary = grBoundary[0]
    censusBoundary = arcpy.ListFeatureClasses(iso+"_admin*")
    censusBoundary.sort()
    censusBoundary = censusBoundary[-1]
    
    # add and calculate growth rate ID on growth rate boundaries
    if len(arcpy.ListFields(grBoundary,'GRID')) == 0:
        arcpy.AddField_management(grBoundary,'GRID','TEXT',"","",50)
        idlen = len(arcpy.GetCount_management(grBoundary)[0])
        i = 1
        with arcpy.da.UpdateCursor(grBoundary, 'GRID') as cursor:
            for row in cursor:
                row[0] = iso+"_"+str(i).zfill(idlen)
                i += 1
                cursor.updateRow(row)
    
    if not "usa" in iso:
        if len(arcpy.ListFields(censusBoundary,'GRID')) == 0:
            arcpy.AddField_management(censusBoundary,'GRID','TEXT',"","",50)
        count = 0
        with arcpy.da.SearchCursor(censusBoundary,'GRID','GRID IS NULL') as cursor:
            for row in cursor:
                count += 1
        
        if count > 0:
            print("  Running join again")
            # convert census boundaries to centroid
            pointFC = os.path.join(scratchGDB,iso+"_points")
            arcpy.FeatureToPoint_management(censusBoundary,pointFC,"INSIDE")
            
            # spatially join growth rates
            spjFC = os.path.join(scratchGDB,iso+"_spj")
            arcpy.SpatialJoin_analysis(pointFC,grBoundary,spjFC)
            
            grDict = {}
            count = 0
            with arcpy.da.SearchCursor(spjFC,['GUBID','GRID_1']) as cursor:
                for row in cursor:
                    if not row[1]:
                        count += 1
                    grDict[row[0]] = row[1]
            if count > 0:
                print("  {} rows do not have a GRID".format(count))
            
            count = 0
            with arcpy.da.UpdateCursor(censusBoundary,['GUBID','GRID']) as cursor:
                for row in cursor:
                    if row[0] in grDict:
                        row[1] = grDict[row[0]]
                        cursor.updateRow(row)
                    else:
                        count += 1
            
            arcpy.Delete_management(pointFC)
            arcpy.Delete_management(spjFC)
    
#    else:
#        # join usa by admin codes (too many to join spatially)
#        grDict = {}
#        with arcpy.da.SearchCursor(grBoundary, ['UCADMIN1','UCADMIN2','GRID']) as cursor:
#            for row in cursor:
#                grDict[row[0]+"_"+row[1]] = row[2]
#        
#        arcpy.AddField_management(censusBoundary,'GRID','TEXT',"","",50)
#        count = 0
#        with arcpy.da.UpdateCursor(censusBoundary,['UCADMIN1','UCADMIN2','GRID']) as cursor:
#            for row in cursor:
#                rid = row[0]+"_"+row[1]
#                if rid in grDict:
#                    row[2] = grDict[rid]
#                    cursor.updateRow(row)
#                else:
#                    count += 1
                    
    if count > 0:
        print("  {} rows did not get a growth rate ID".format(count))


