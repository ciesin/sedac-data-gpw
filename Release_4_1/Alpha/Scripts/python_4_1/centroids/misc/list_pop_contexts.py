#Jane Mills
#3/23/2017
#list all the boundary and pop contexts

# Import Libraries
import arcpy, os, csv

bounds = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'
tables = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\tables\lookup_tables.gdb'

csvPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\centroids\pop_contexts.csv'
csvMem = csv.writer(open(csvPath,"wb"))
csvMem.writerow(['ISO','UBID','context'])

arcpy.env.workspace = bounds
boundList = arcpy.ListFeatureClasses()
boundList.sort()

arcpy.env.workspace = tables
tableList = arcpy.ListTables()
tableList.sort()

for bound in boundList:
    iso = bound[:3]
    boundPath = os.path.join(bounds, bound)

    print iso
    contexts = {}
    ubids = {}

    #check boundary contexts
    with arcpy.da.SearchCursor(boundPath,['UBID','BOUNDARY_CONTEXT']) as cursor:
        for row in cursor:
            ubids[row[0]] = "Present"
            if not row[1] is None :
                contexts[row[0]] = row[1]
    
    isoTables = filter(lambda x: iso in x, tableList)
    if len(isoTables) == 1:
        table = os.path.join(tables,isoTables[0])

        #Check pop contexts
        with arcpy.da.SearchCursor(table,['UBID','POP_CONTEXT'],"POP_CONTEXT IS NOT NULL") as cursor:
            for row in cursor:
                if row[0] in ubids:
                    if row[0] in contexts:
                        pass
                    else:
                        csvMem.writerow([iso,row[0],row[1]])

    del contexts
    del ubids

print 'done'

