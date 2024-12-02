#Jane Mills
#3/23/2017
#Fill in un densities
#What do we do about the units with zero area and pop?

# Import Libraries
import arcpy, os, csv

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
centroidsUSA = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data_usa.gdb'
csvPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\centroids\no_area.csv'

csvMem = csv.writer(open(csvPath,"wb"))
csvMem.writerow(['ISO','UBID','pop'])

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()

arcpy.env.workspace = centroidsUSA
usaList = arcpy.ListFeatureClasses()

for f in usaList:
    fcList.append(f)

fields = ['UBID','CONTEXT','TOTAL_A_KM','WATER_A_KM','LAND_A_KM','WATER_CODE','UN_2010_E']

fcList.sort()
for fc in fcList:
    if fc[:3] == 'usa':
        iso = fc[:6]
        fcPath = os.path.join(centroidsUSA,fc)
    else:
        iso = fc[:3]
        fcPath = os.path.join(centroids, fc)
    print iso

    with arcpy.da.SearchCursor(fcPath,fields,"UN_2010_E IS NOT NULL") as cursor:
        for row in cursor:
            if row[4] == 0 and row[6] > 0:
                if row[5] == 'IW':
                    pass
                else:
                    csvMem.writerow([iso,row[0],row[6]])

print 'done'
