#Jane Mills
#3/23/2017
#list all the boundary and pop contexts

# Import Libraries
import arcpy, os, csv

bounds = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'
tables = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\tables\lookup_tables.gdb'
csvPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\centroids\context_units.csv'
usaBounds = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\tiled_countries\usa.gdb'

csvMem = csv.writer(open(csvPath,"wb"))
csvMem.writerow(['context','num units'])

arcpy.env.workspace = bounds
boundList = arcpy.ListFeatureClasses()
boundList.sort()

arcpy.env.workspace = tables

contexts = {}

for bound in boundList:
    iso = bound[:3]
    boundPath = os.path.join(bounds, bound)

    print iso

    #check boundary contexts
    with arcpy.da.SearchCursor(boundPath,['UBID','BOUNDARY_CONTEXT'],"BOUNDARY_CONTEXT IS NOT NULL") as cursor:
        for row in cursor:
            if row[1] in contexts:
                contexts[row[1]] += 1
            else:
                contexts[row[1]] = 1
    
    tableList = arcpy.ListTables(iso+"*")
    if len(tableList) == 1:
        table = tableList[0]

        #Check pop contexts
        with arcpy.da.SearchCursor(table,['UBID','POP_CONTEXT'],"POP_CONTEXT IS NOT NULL") as cursor:
            for row in cursor:
                if row[1] in contexts:
                    contexts[row[1]] += 1
                else:
                    contexts[row[1]] = 1

arcpy.env.workspace = usaBounds
boundList = arcpy.ListFeatureClasses()
boundList.sort()

for bound in boundList:
    if len(bound) == 29:
        print bound
        with arcpy.da.SearchCursor(bound,['UBID','BOUNDARY_CONTEXT'],"BOUNDARY_CONTEXT IS NOT NULL") as cursor:
            for row in cursor:
                if row[1] in contexts:
                    contexts[row[1]] += 1
                else:
                    contexts[row[1]] = 1

for key in contexts:
    csvMem.writerow([key,contexts[key]])

print 'done'
