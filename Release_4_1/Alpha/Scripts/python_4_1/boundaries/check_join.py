#Jane Mills
#1/13/2017
#Check that UBID and USCID are unique in lookup tables
#Check that UBID is unique in boundaries
#Validate join

import os, arcpy

tableGDB = r'F:\GPW\calculate_gubids\lookup_tables.gdb'
boundGDB = r'F:\GPW\calculate_gubids\country_boundaries_hi_res_1_13.gdb'
#tableGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\lookup_tables.gdb'
#boundGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\from_sde\country_boundaries_hi_res_1_13.gdb'

arcpy.env.workspace = tableGDB

tableList = arcpy.ListTables()
tableList.sort()

for table in tableList:
    iso = table[:3]
    admin = table[9]
    print iso

    ubidList = []
    ubidListBound = []
    uscidList = []

    tFields = ['USCID','UBID']
    bFields = ['UBID','BOUNDARY_CONTEXT']

    #check that uscids and ubids are unique, all units without UBIDs have pop context
    with arcpy.da.SearchCursor(table,tFields) as cursor:
        for row in cursor:
            ubid = row[1]
            uscid = row[0]
            #check that uscids and ubids are unique, all units have UBIDs
            if uscid == '' or uscid is None:
                print "missing USCID. UBID: " + ubid
            else:
                if uscid in uscidList:
                    print "duplicate USCID in lookup table: " + uscid
                else:
                    uscidList.append(uscid)
            if ubid == '' or ubid is None:
                print "UBID missing, no pop context. USCID: " + uscid
            else:
                if ubid in ubidList:
                    print "duplicate UBID in lookup table: " + ubid
                else:
                    ubidList.append(ubid)

    #check that ubids in the boundary are unique and are in the ubid list from the table
    boundary = os.path.join(boundGDB,iso+'_admin'+admin+'_boundaries_2010')
    with arcpy.da.SearchCursor(boundary,bFields) as cursor:
        for row in cursor:
            ubid = row[0]
            if ubid == '' or ubid is None:
                print "missing UBID"
            else:
                if not ubid in ubidList:
                    if row[1] == '' or row[1] is None:
                        print "boundary UBID is not in table, no boundary context: " + ubid
                if ubid in ubidListBound:
                    print "duplicate UBID in lookup table: " + ubid
                else:
                    ubidListBound.append(ubid)
