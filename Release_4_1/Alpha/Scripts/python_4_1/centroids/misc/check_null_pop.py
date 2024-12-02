#Jane Mills
#7/25/2018

import arcpy

centroids = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\country_data.gdb'
#gridding = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

arcpy.env.workspace = centroids
#arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

fields = ['CONTEXT','WATER_CODE','UN_2000_E']
#fields = ['CONTEXT','WATER_CODE','UNE_ATOTPOPBT_2000']

##for fc in fcList:
##    iso = fc[:-10]
##    print iso
##    nullpopunits = 0
##    nullpopunitscontext = 0
##    nullpopwater = 0
##    with arcpy.da.SearchCursor(fc,fields,fields[2] + " IS NULL") as cursor:
##        for row in cursor:
##            if row[0] > 0:
##                nullpopunitscontext += 1
##            if row[1] == 'IW':
##                nullpopwater += 1
##            if row[0] == 0 and row[1] == 'L':
##                nullpopunits += 1
##
##    if nullpopunits > 0:
##        print "{} units with null pop and no context/water".format(nullpopunits)
##    if nullpopwater > 0:
##        print "{} water units with null pop".format(nullpopwater)
##    if nullpopunitscontext > 0:
##        print "{} context units with null pop".format(nullpopunitscontext)

for fc in fcList:
    iso = fc[:-10]
    if not iso[:3] == 'usa':
        print iso
        contextpop = {}
        waterpop = 0
        bothunits = 0
        with arcpy.da.SearchCursor(fc,['CONTEXT','WATER_CODE','UN_2010_E'],"CONTEXT > 0 OR WATER_CODE = 'IW'") as cursor:
            for row in cursor:
                if row[0] > 0:
                    if row[0] in contextpop:
                        contextpop[row[0]] += row[2]
                    else:
                        contextpop[row[0]] = row[2]
                if row[1] == 'IW':
                    waterpop += row[2]
                if row[0] > 0 and row[1] == 'IW':
                    bothunits += 1

        if len(contextpop) > 0:
            for key in contextpop:
                print "{} people in context {} units".format(contextpop[key], key)
        if waterpop > 0:
            print "{} people in water units".format(waterpop)
        if bothunits > 0:
            print "{} water units with context".format(bothunits)
