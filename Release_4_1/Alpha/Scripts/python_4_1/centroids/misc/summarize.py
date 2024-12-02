#Jane Mills
#3/23/2017
#Fill in pop counts for units with data context
#run the script without changing the tables and make sure your sums add up
#otherwise you'll lose all your work

# Import Libraries
import arcpy, os, csv

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
centroidsUSA = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data_usa.gdb'
csvPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\centroids\misc\counts.csv'

csvMem = csv.writer(open(csvPath,"wb"))
csvMem.writerow(['ISO','field','UN_2000_E_before', 'UN_2005_E_before', 'UN_2010_E_before', 'UN_2015_E_before',
                 'UN_2020_E_before', 'B_2010_E_before', 'F_2010_E_before', 'M_2010_E_before'])

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()

arcpy.env.workspace = centroidsUSA
usaList = arcpy.ListFeatureClasses()
for f in usaList:
    fcList.append(f)

fields = ['CONTEXT','WATER_CODE','UN_2000_E','UN_2005_E','UN_2010_E','UN_2015_E',
          'UN_2020_E','B_2010_E','F_2010_E','M_2010_E']

fcList.sort()
for fc in fcList:
    if fc[:3] = 'usa':
        iso = fc[:6]
        cenPath = os.path.join(centroidsUSA,fc)
    else:
        iso = fc[:3]
        cenPath = os.path.join(centroids,fc)
    print iso
    
    total1 = {}
    total2 = {}
    with arcpy.da.SearchCursor(cenPath,[f,'CONTEXT','WATER_CODE','B_2010_E']) as cursor:
        for row in cursor:
            if not iso in total1:
                total1 += row[0]
            if row[1] == 205:
                total2 += 0
            if row[1] in [201,202,203,204,206]:
                pass
            #Water units with no pop filled in with zeros
            if row[2] == 'IW' and row[0] == 0:
                total2 += 0

            #Fill "missing age/sex data" with Nulls
            if row[0] == 207 and row[3] > 0:
                #if it's missing sex data, it'll be missing age data as well
                if row[13] == 0 and row[14] == 0:
                    row[13] = None
                    row[14] = None
                if sum(row[15:]) == 0:
                    for i in range(15,len(fields)):
                        row[i] = None
        csvMem.writerow([iso,f,total1,total2])

print 'done'
