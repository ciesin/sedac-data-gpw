#Jane Mills
#1/13/2017
#Calculate pop context from census tables
import os, arcpy

lookupGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\lookup_tables.gdb'
censusGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\highlevel_census.gdb'

arcpy.env.workspace = censusGDB
#arcpy.env.overwriteOutput = True

tableList = arcpy.ListTables()
tableList.sort()

arcpy.env.workspace = lookupGDB

for table in tableList:
    iso = table[:3]
    print iso
    tablePath = os.path.join(censusGDB,table)

    fieldList = arcpy.ListFields(tablePath,"POP_CONTEXT")
    if len(fieldList) == 1:
        #go find the lookup table
        lookupList = arcpy.ListTables(iso+"*")
        if not len(lookupList) == '0':
            lookup = lookupList[0]

            #build dictionary of pop context
            pcDict = {}
            with arcpy.da.SearchCursor(tablePath,['USCID','POP_CONTEXT'],"POP_CONTEXT IS NOT NULL") as cursor:
                for row in cursor:
                    pcDict[row[0]] = row[1]

            #calculate the pop context
            with arcpy.da.UpdateCursor(lookup,['USCID','POP_CONTEXT']) as cursor:
                for row in cursor:
                    uscid = row[0]
                    if uscid in pcDict:
                        row[1] = pcDict[uscid]
                    else:
                        pass
                    cursor.updateRow(row)
            print "calculated pop context"
        else:
            print "census table not found"
