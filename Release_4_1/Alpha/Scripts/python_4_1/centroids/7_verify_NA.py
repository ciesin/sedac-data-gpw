#Jane Mills
#3/23/2017
#Check that every unit filled with NA has a boundary context

# Import Libraries
import arcpy, os, csv

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
bounds = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'
csvPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\centroids\NA_units.csv'

csvMem = csv.writer(open(csvPath,"wb"))
csvMem.writerow(['ISO','UBID'])

arcpy.env.workspace = bounds
boundList = arcpy.ListFeatureClasses()
boundList.sort()

for bound in boundList:
    if bound[:3] == 'usa':
        iso = 'usa_'+bound[3:5]
    else:
        iso = bound[:3]
    cenPath = os.path.join(centroids,iso+"_centroids")
    
    level = bound[-17]

    if level == '0':
        pass
    else:
        print iso
        #check boundary contexts
        bcDict = {}
        with arcpy.da.SearchCursor(bound,['UBID','BOUNDARY_CONTEXT'],"BOUNDARY_CONTEXT IS NOT NULL") as cursor:
            for row in cursor:
                bcDict[row[0]] = row[1]

        #Check our centroids
        with arcpy.da.SearchCursor(cenPath,['UBID','NAME1']) as cursor:
            for row in cursor:
                ubid = row[0]
                if row[1] == 'NA':
                    if ubid in bcDict:
                        pass
                    else:
                        csvMem.writerow([iso,ubid])

        del bcDict

print 'done'
