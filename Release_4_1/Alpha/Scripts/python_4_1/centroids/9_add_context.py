#Jane Mills
#3/23/2017
#Add the data context (boundary context supercedes pop context - it's more specific)

# Import Libraries
import arcpy, os, csv

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
boundaries = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'
tables = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\tables\lookup_tables.gdb'

lookup = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\ancillary.gdb\context_codes'
contextDict = {}
with arcpy.da.SearchCursor(lookup,['context_orig','CONTEXT','CONTEXT_NM']) as cursor:
    for row in cursor:
        contextDict[row[0]] = row[1:]

arcpy.env.workspace = boundaries
boundList = arcpy.ListFeatureClasses()
boundList.sort()

arcpy.env.workspace = tables
tableList = arcpy.ListTables()
tableList.sort()

for bound in boundList:
    iso = bound[:3]
    print iso
    codesDict = {}
    waterDict = {}
    
    boundPath = os.path.join(boundaries,bound)
    cenPath = os.path.join(centroids,iso+"_centroids")

    isoTables = filter(lambda x: iso in x, tableList)
    if len(isoTables) == 1:
        tablePath = os.path.join(tables,isoTables[0])

        #check pop contexts
        with arcpy.da.SearchCursor(tablePath,['UBID','POP_CONTEXT'],"POP_CONTEXT IS NOT NULL") as cursor:
            for row in cursor:
                codesDict[row[0]] = row[1]
    if not len(isoTables) == 1:
        print "no table found"

    #check boundary contexts
    with arcpy.da.SearchCursor(boundPath,['UBID','BOUNDARY_CONTEXT'],"BOUNDARY_CONTEXT IS NOT NULL") as cursor:
        for row in cursor:
            if row[1] == 7 or row[1] == 8:
                waterDict[row[0]] = "IW"

            if row[0] in codesDict:
                if row[1] == 8:
                    pass
                else:
                    codesDict[row[0]] = row[1]
                #print "found duplicates:", row[0], row[1], codesDict[row[0]]
            if not row[0] in codesDict:
                codesDict[row[0]] = row[1]

    #Add to centroids
    with arcpy.da.UpdateCursor(cenPath,['UBID','CONTEXT','CONTEXT_NM','WATER_CODE']) as cursor:
        for row in cursor:
            ubid = row[0]
            if ubid in waterDict:
                row[3] = "IW"
            if not ubid in waterDict:
                row[3] = "L"

            if ubid in codesDict:
                code = codesDict[ubid]
                if code in contextDict:
                    context = contextDict[code]
                    row[1] = context[0]
                    row[2] = context[1]
                elif code == 7:
                    pass
                else:
                    print "can't find matching code:", row[0], code
            cursor.updateRow(row)

    del codesDict

print 'done'
