#Jane Mills
#3/23/2017
#Calculate the name fields from the geo tables
#coerce to ASCII (put a note for the users somewhere)

# Import Libraries
import arcpy, os, unicodedata

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
tables = r'\\Dataserver0\gpw\GPW4\Release_4_0\Beta\Preprocessing\Country\USA\Ingest\Census\USA_geo_names.gdb'
stateTable = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\ancillary.gdb\usa_states'

stateDict = {}
with arcpy.da.SearchCursor(stateTable,['STUSPS10','NAME10']) as cursor:
    for row in cursor:
        stateDict[row[0]] = row[1]

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses("usa*")
fcList.sort()

arcpy.env.workspace = tables

for fc in fcList:
    state = fc[4:6].upper()
    stateName = stateDict[state]
    fcPath = os.path.join(centroids,fc)
    print state, stateName

    tableList = arcpy.ListTables(state+"*")
    if len(tableList) == 1:
        table = tableList[0]

        #build a dictionary of Names (replacing Null values with NA, coercing unicode to ascii)
        nameDict = {}
        with arcpy.da.SearchCursor(table,['UBID','NAME2','NAME3','NAME4']) as cursor:
            for row in cursor:
                names = []
                for n in row[1:]:
                    if n is None:
                        names.append("NA")
                    elif isinstance(n,str):
                        names.append(n)
                    elif isinstance(n,unicode):
                        n1 = unicodedata.normalize('NFKD',n)
                        n2 = n1.encode('ASCII','ignore')
                        names.append(n2)
                nameDict[row[0]] = names

        #Write out names to our centroids
        with arcpy.da.UpdateCursor(fcPath,['UBID','NAME1','NAME2','NAME3','NAME4','NAME5','NAME6']) as cursor:
            for row in cursor:
                ubid = row[0]
                if ubid in nameDict:
                    nameList = nameDict[ubid]
                    row[1] = stateName
                    row[2] = nameList[0]
                    row[3] = nameList[1]
                    row[4] = nameList[2]
                    row[5] = "Block "+ubid[-4:]
                    row[6] = "NA"
                    cursor.updateRow(row)
                else:
                    print row[0]

        del nameDict

    elif len(tableList) == 0:
        print "table not found"

print 'done'
