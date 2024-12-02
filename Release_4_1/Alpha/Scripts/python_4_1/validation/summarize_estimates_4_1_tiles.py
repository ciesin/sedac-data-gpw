#Jane Mills
#3/9/17
#summarize rasters and compare to tables

import arcpy, os, csv
from arcpy import env

rootFolder = r'D:\gpw\release_4_1\process'

csvPath = open(r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\validation\country_counts_6_13.csv',"wb")
csvFile = csv.writer(csvPath)
csvFile.writerow(("ISO","tile","field","sum"))
#isoList = ['aus','bra','can','chn','grl','ind','kaz','rus']
#isoList = ['grl']
isoList = ['can','chn','ind','kaz','rus']

env.workspace = rootFolder
gdbList = arcpy.ListWorkspaces("","FILEGDB")

for iso in isoList:
    print iso
    gdbs = gdbs = filter(lambda x: os.path.basename(x)[:3] == iso, gdbList)

    for gdb in gdbs:
        tile = os.path.basename(gdb)
        print tile
        env.workspace = gdb
        table = arcpy.ListTables("*estimates")[0]
        fieldList = [f.name for f in arcpy.ListFields(table,"*","DOUBLE")]
        for field in fieldList:
            if field[-3:] == "DSM":
                pass
            else:
                print field
                tCount = 0
                with arcpy.da.SearchCursor(table,field) as cursor:
                    for row in cursor:
                        tCount += row[0]

                csvFile.writerow((iso,tile,field,str(tCount)))

csvPath.close()
print "done"

