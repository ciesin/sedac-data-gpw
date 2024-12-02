import arcpy, os
rootFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries'
centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'

isos = ['aus','bra','chn','ind','kaz']

for iso in isos:
    print iso
    cen = os.path.join(centroids,iso+'_centroids')
    inGDB = os.path.join(rootFolder,'working',iso+'.gdb')

    arcpy.env.workspace = inGDB
    inFC = arcpy.ListFeatureClasses()[0]

    names = {}

    with arcpy.da.SearchCursor(cen,["GUBID","NAME1"]) as cursor:
        for row in cursor:
            names[row[0]] = row[1]

    with arcpy.da.UpdateCursor(inFC,['GUBID','tile']) as cursor:
        for row in cursor:
            if row[0] in names:
                name = names[row[0]]
                row[1] = name.replace(" ","").lower()
                cursor.updateRow(row)
            else:
                print row[0], "not in centroids"

    del names

print "done"

