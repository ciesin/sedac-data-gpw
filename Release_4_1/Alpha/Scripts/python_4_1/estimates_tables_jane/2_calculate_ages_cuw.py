#Jane Mills
#5/12/17
#GPWv4
#add up ages

import arcpy, os, numpy, datetime
from arcpy import env
scriptTime = datetime.datetime.now()

rootFolder = r'D:\gpw\release_4_1\loading\processed'
isoList = ['bfa','bhr','blr','caf','col','cuw','dji','eri','gab','grd','irq','lbn','mdg','mhl','prt','rus','som','tca','tjk','tkm','ukr','uzb']
gdbList = [os.path.join(rootFolder,iso+'.gdb') for iso in isoList]

for gdb in gdbList:    
    env.workspace = gdb
    env.overwriteOutput = True
    iso = os.path.basename(gdb)[:-4]

    #Find table
    estList = arcpy.ListTables("*estimates")
    if len(estList) == 1:
        estTable = estList[0]
        estMem = 'in_memory' + os.sep + iso
        arcpy.CopyRows_management(estTable,estMem)

        #calculate PLUS categories
        topField = [f.name for f in arcpy.ListFields(estMem,"E_A*PLUSBT_2010")]
        topField.sort()
        if len(topField) == 0:
            topField = fieldList[-1]
            topAge = int(topField[-14:-11])
            arcpy.AlterField_management(estMem,topField[:-7]+"BT_2010",topField[:-11]+"PLUSBT_2010")
            arcpy.AlterField_management(estMem,topField[:-7]+"FT_2010",topField[:-11]+"PLUSFT_2010")
            arcpy.AlterField_management(estMem,topField[:-7]+"MT_2010",topField[:-11]+"PLUSMT_2010")
        else:
            topAge = int(topField[-1][-14:-11])

        if topAge > 65:
            for i in reversed(range(65,topAge,5)):
                age = str(i).zfill(3)
                top = str(i+4).zfill(3)
                nextAge = str(i+5).zfill(3)

                ageFields = ["E_A"+age+"PLUSBT_2010","E_A"+age+"PLUSFT_2010","E_A"+age+"PLUSMT_2010",
                             "E_A"+age+"_"+top+"BT_2010","E_A"+age+"_"+top+"FT_2010","E_A"+age+"_"+top+"MT_2010",
                             "E_A"+nextAge+"PLUSBT_2010","E_A"+nextAge+"PLUSFT_2010","E_A"+nextAge+"PLUSMT_2010"]

                with arcpy.da.UpdateCursor(estMem,ageFields,"E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
                    for row in cursor:
                        row[0] = row[3]+row[6]
                        row[1] = row[4]+row[7]
                        row[2] = row[5]+row[8]
                        cursor.updateRow(row)

        print iso+": plus"

        arcpy.CopyRows_management(estMem,estTable+"_reprocessed")


print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
