#Jane Mills
#5/12/17
#GPWv4
#add up ages

import arcpy, os, datetime
from arcpy import env
scriptTime = datetime.datetime.now()

rootFolder = r'D:\gpw\release_4_1\loading\processed'
isoList = ['bfa','bhr','blr','caf','col','cuw','dji','eri','gab','grd','irq',
           'lbn','mdg','mhl','prt','rus','som','tca','tjk','tkm','ukr','uzb']
gdbList = [os.path.join(rootFolder,iso+'.gdb') for iso in isoList]

#env.workspace = rootFolder
#env.overwriteOutput = True

#gdbList = arcpy.ListWorkspaces("*","FILEGDB")
#gdbList.sort()

for gdb in gdbList:    
    env.workspace = gdb
    iso = os.path.basename(gdb)[:-4]
    print iso

    #Find tables
    estList = arcpy.ListTables("*estimates_reprocessed")
    oldList = arcpy.ListTables("*estimates")
    if len(estList) == 1 and len(oldList) == 1:
        estTable = estList[0]
        oldTable = oldList[0]

        arcpy.Delete_management(oldTable)
        print "deleted"
        arcpy.Rename_management(estTable,estTable[:-12])
        print "renamed"


print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
