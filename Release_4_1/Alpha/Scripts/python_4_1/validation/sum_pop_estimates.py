import arcpy, numpy

root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

arcpy.env.workspace = root
fcList = arcpy.ListFeatureClasses()
fcList.sort()

headers = ['E_ATOTPOPBT_1975','E_ATOTPOPBT_1990','E_ATOTPOPBT_2000','E_ATOTPOPBT_2005','E_ATOTPOPBT_2010',
           'E_ATOTPOPBT_2015','E_ATOTPOPBT_2020','UNE_ATOTPOPBT_1975','UNE_ATOTPOPBT_1990','UNE_ATOTPOPBT_2000',
           'UNE_ATOTPOPBT_2005','UNE_ATOTPOPBT_2010','UNE_ATOTPOPBT_2015','UNE_ATOTPOPBT_2020']

for fc in fcList:
    iso = fc[:3]
    if not iso == "usa":
        print iso

        totals = numpy.array([0.0]*14)
        with arcpy.da.SearchCursor(fc,headers,"E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
            for row in cursor:
                totals += numpy.array(row)

        for t in totals:
            print t


