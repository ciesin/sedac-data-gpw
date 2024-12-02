#Jane Mills
#3/23/2017
#Add areas to centroids

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'
orig = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'
template = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\ancillary.gdb\gridding_boundary_template'

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()
fcList.sort()

arcpy.env.workspace = orig
origList = arcpy.ListFeatureClasses()

arcpy.env.overwriteOutput = True

fields = ['GUBID','ISOALPHA','COUNTRYNM','NAME1','NAME2','NAME3','NAME4','NAME5','NAME6','CONTEXT','CONTEXT_NM','WATER_CODE']

for fc in fcList[30:]:
    if fc[:3] == 'usa':
        iso = fc[:5]
    else:
        iso = fc[:3]
    cenPath = os.path.join(centroids,iso+"_centroids")
    print iso

    origFCs = filter(lambda x: iso+"_admin" in x, origList)
    origFC = os.path.join(orig,origFCs[0])

    outFC = os.path.join(gridding,os.path.basename(origFC))
    arcpy.CopyFeatures_management(template,outFC)
    arcpy.Append_management(origFC,outFC,"NO_TEST")

    dataDict = {}
    with arcpy.da.SearchCursor(cenPath,fields) as cursor:
        for row in cursor:
            dataDict[row[0]] = row[1:]

    #Add to centroids
    with arcpy.da.UpdateCursor(outFC,fields) as cursor:
        for row in cursor:
            if row[0] in dataDict:
                row[1:] = dataDict[row[0]]
                cursor.updateRow(row)
            else:
                print "did not find gubid:", row[0]

    del dataDict


print 'done'
