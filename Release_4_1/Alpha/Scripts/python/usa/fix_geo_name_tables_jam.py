#Jane Mills
#2/19/2016
#Get the USA names out of the geo tables and update the name tables

import arcpy, os
from arcpy import env

geoGDB = r'\\Dataserver0\gpw\GPW4\Release_4_0\Beta\Preprocessing\Country\USA\Ingest\Census\state_geo.gdb'
finalGDB = r'\\Dataserver0\gpw\GPW4\Release_4_0\Beta\Preprocessing\Country\USA\Ingest\Census\USA_geo_names.gdb'

env.workspace = finalGDB
env.overwriteOutput = True

tableList = arcpy.ListTables("*")
tableList.sort()

for table in tableList:
    print table
    state = table[:2]
    
    geotable = os.path.join(geoGDB,state+"geo2010")

    #Make dictionaries of names
    dict2 = {}
    dict3 = {}
    dict4 = {}
    
    with arcpy.da.SearchCursor(geotable,['SUMLEV','STATE','COUNTY','TRACT','BLKGRP','NAME']) as cursor:
        for row in cursor:
            if row[0] == '050':
                ID2 = str(row[1])+str(row[2])
                # special condition for special character in Dona Ana County
                try:
                    dict2[ID2] = str(row[5])
                except:
                    dict2[ID2] = row[5].replace(u'\xb1',u'\xf1')
                    
            elif row[0] == '140':
                ID3 = str(row[1])+str(row[2])+str(row[3])
                dict3[ID3] = str(row[5])
            elif row[0] == '150':
                ID4 = str(row[1])+str(row[2])+str(row[3])+str(row[4])
                dict4[ID4] = str(row[5])
    
    #Update name tables with dictionaries
    with arcpy.da.UpdateCursor(table,['UBID','NAME2','NAME3','NAME4']) as cursor:
        for row in cursor:
            UBID = row[0]
            ID2 = UBID[3:8]
            ID3 = UBID[3:14]
            ID4 = UBID[3:15]

            row[1] = dict2[ID2]
            row[2] = dict3[ID3]
            row[3] = dict4[ID4]
            
            cursor.updateRow(row)

    #Delete the dictionaries
    del dict2
    del dict3
    del dict4

    print "completed",table

