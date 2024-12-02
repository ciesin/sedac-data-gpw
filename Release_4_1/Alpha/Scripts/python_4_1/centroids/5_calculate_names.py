#Jane Mills
#3/23/2017
#Calculate the name fields from the lookup tables
#coerce to ASCII (put a note for the users somewhere)
#truncate long field names (sorry)

# Import Libraries
import arcpy, os, unicodedata

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
tables = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\tables\lookup_tables.gdb'

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()
fcList.sort()

arcpy.env.workspace = tables

#Do all countries except USA
for fc in fcList:
    iso = fc[:3]
    if iso == 'usa':
        pass
    else:
        fcPath = os.path.join(centroids,fc)
        
        print iso

        tableList = arcpy.ListTables(iso+"*")
        if len(tableList) == 1:
            table = tableList[0]

            #build a dictionary of Names (replacing Null values with NA, coercing unicode to ascii)
            nameDict = {}
            with arcpy.da.SearchCursor(table,['UBID','NAME1','NAME2','NAME3','NAME4','NAME5','NAME6']) as cursor:
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
            noCount = 0
            with arcpy.da.UpdateCursor(fcPath,['UBID','NAME1','NAME2','NAME3','NAME4','NAME5','NAME6']) as cursor:
                for row in cursor:
                    if row[0] in nameDict:
                        names = nameDict[row[0]]
                        for i in range(len(names)):
                            n = names[i]
                            if len(n) > 100:
                                names[i] = n[:100]
                        row[1] = names[0]
                        row[2] = names[1]
                        row[3] = names[2]
                        row[4] = names[3]
                        row[5] = names[4]
                        row[6] = names[5]
                    else:
                        noCount += 1
                        row[1] = "NA"
                        row[2] = "NA"
                        row[3] = "NA"
                        row[4] = "NA"
                        row[5] = "NA"
                        row[6] = "NA"

                    cursor.updateRow(row)

            del nameDict
            print noCount

        elif len(tableList) == 0:
            print "table not found"

            with arcpy.da.UpdateCursor(fcPath,['NAME1','NAME2','NAME3','NAME4','NAME5','NAME6']) as cursor:
                for row in cursor:
                    row[0] = 'NA'
                    row[1] = 'NA'
                    row[2] = 'NA'
                    row[3] = 'NA'
                    row[4] = 'NA'
                    row[5] = 'NA'
                    cursor.updateRow(row)



print 'done'
