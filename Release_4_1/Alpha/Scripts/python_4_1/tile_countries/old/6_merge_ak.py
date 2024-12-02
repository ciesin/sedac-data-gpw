import arcpy, os
from arcpy import env

inFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\process\usa_ak.gdb'

arcpy.env.workspace = outGDB

tableList = arcpy.ListTables()
tableList.sort()

gdbs = ['usaakeast.gdb','usaakwestne.gdb','usaakwestnw.gdb','usaakwestse.gdb']

for t in tableList[1:]:
    print t
    outTable = os.path.join(outGDB,t)

    for gdb in gdbs:
        aTable = os.path.join(inFolder,gdb,gdb[:-4]+t[5:])
        arcpy.Append_management(aTable,outTable,"NO_TEST")



