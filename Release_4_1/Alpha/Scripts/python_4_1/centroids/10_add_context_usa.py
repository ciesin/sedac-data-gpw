#Jane Mills
#3/23/2017
#Add the data context

# Import Libraries
import arcpy, os, csv

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data_usa.gdb'
boundaries = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\tiled_countries\usa.gdb'

lookup = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\ancillary.gdb\context_codes'
contextDict = {}
with arcpy.da.SearchCursor(lookup,['context_orig','CONTEXT','CONTEXT_NM']) as cursor:
    for row in cursor:
        contextDict[row[0]] = row[1:]

arcpy.env.workspace = boundaries
boundList = arcpy.ListFeatureClasses()
boundList.sort()

for bound in boundList:
    if len(bound) == 29:
        iso = bound[:6]
        print iso
        
        cenPath = os.path.join(centroids,iso+"_centroids")

        #check boundary contexts
        codesDict = {}
        with arcpy.da.SearchCursor(bound,['UBID','BOUNDARY_CONTEXT'],"BOUNDARY_CONTEXT IS NOT NULL") as cursor:
            for row in cursor:
                if row[0] in codesDict:
                    print "found duplicates:", row[0], row[1], codesDict[row[0]]
                else:
                    codesDict[row[0]] = row[1]

        #Add to centroids
        with arcpy.da.UpdateCursor(cenPath,['UBID','CONTEXT','CONTEXT_NM','WATER_CODE']) as cursor:
            for row in cursor:
                ubid = row[0]
                if ubid in codesDict:
                    code = codesDict[ubid]
                    if code == 7:
                        row[3] = "IW"
                    elif code in contextDict:
                        context = contextDict[code]
                        row[1] = context[0]
                        row[2] = context[1]
                    else:
                        print "can't find matching code:", row[0], code
                else:
                    row[3] = "L"
                cursor.updateRow(row)

        del codesDict

    else:
        pass

print 'done'

