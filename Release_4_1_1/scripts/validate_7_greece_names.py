#Jane Mills
#fix greek names

import arcpy

centroids = r'F:\gpw\v411\centroids\original\greece.gdb\grc_centroids'
outCentroids = r'F:\gpw\v411\centroids\original\country_data.gdb\grc_centroids'
inTable = r'\\Dataserver1\gpw\GPW4\Release_411\validation\scratch.gdb\grc_admin5_english'

fList = ['UBID','NAME1','NAME2','NAME3','NAME4','NAME5']

nameDict = {}
with arcpy.da.SearchCursor(inTable,fList) as cursor:
    for row in cursor:
        nameDict[str(row[0])] = row[1:]

with arcpy.da.UpdateCursor(centroids,fList) as cursor:
    for row in cursor:
        row[1:] = nameDict[row[0]]
        cursor.updateRow(row)

fList = ['GUBID','NAME1','NAME2','NAME3','NAME4','NAME5']
nameDict = {}
with arcpy.da.SearchCursor(centroids,fList) as cursor:
    for row in cursor:
        nameDict[row[0]] = row[1:]

with arcpy.da.UpdateCursor(outCentroids,fList) as cursor:
    for row in cursor:
        row[1:] = nameDict[row[0]]
        cursor.updateRow(row)
        
outCentroids = r'F:\gpw\v411\centroids\original\merged_data.gdb\Europe_centroids'
outCentroids = r'F:\gpw\v411\centroids\original\merged_data.gdb\Global_centroids'
outCentroids = r'\\Dataserver1\gpw\GPW4\Release_411\data\centroids\country_data.gdb\grc_centroids'
outCentroids = r'\\Dataserver1\gpw\GPW4\Release_411\data\centroids\merged_data.gdb\Europe_centroids'
outCentroids = r'\\Dataserver1\gpw\GPW4\Release_411\data\centroids\merged_data.gdb\Global_centroids'
outCentroids = r'F:\gpw\v411\centroids\global\gpw_v4_admin_unit_center_points_population_estimates_rev11_europe.gdb\gpw_v4_admin_unit_center_points_population_estimates_rev11_europe'
outCentroids = r'F:\gpw\v411\centroids\global\gpw_v4_admin_unit_center_points_population_estimates_rev11_global.gdb\gpw_v4_admin_unit_center_points_population_estimates_rev11_global'
outCentroids = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\gridding_boundaries.gdb\grc_admin5_boundaries_2010'

with arcpy.da.UpdateCursor(outCentroids,fList,"ISOALPHA = 'GRC'") as cursor:
    for row in cursor:
        row[1:] = nameDict[row[0]]
        cursor.updateRow(row)

