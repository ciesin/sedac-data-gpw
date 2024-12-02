#Jane Mills
#5/12/17
#GPWv4
#add up ages

import arcpy, os, numpy, datetime
from arcpy import env
scriptTime = datetime.datetime.now()

rootFolder = r'D:\gpw\release_4_1\loading\processed'
#done: 'bfa','bhr','blr','caf','col','cuw','dji','eri','gab','grd','irq','lbn','mdg','mhl','rus','som','tca','tjk','tkm','ukr','uzb'

isoList = ['prt']
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

        #Add BT age fields
        fieldList  = []
        fields = arcpy.ListFields(estMem,"E_A*FT_2010")
        for f in fields:
            if not "TOTPOP" in f.name and not "015_049" in f.name:
                fieldList.append(f.name)

        #calculate BT ages
        fieldList.sort()
        finalFields = [f[:-7]+"BT_2010" for f in fieldList] + [f[:-7]+"FT_2010" for f in fieldList] + [f[:-7]+"MT_2010" for f in fieldList]
        with arcpy.da.UpdateCursor(estMem,finalFields,"E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
            for row in cursor:
                row[:len(finalFields)/3] = list(numpy.add(row[len(finalFields)/3:-len(finalFields)/3],row[-len(finalFields)/3:]))
                cursor.updateRow(row)

        print iso+": BT"

        #calculate PLUS categories
        topField = [f.name for f in arcpy.ListFields(estMem,"E_A*PLUSBT_2010")]
        if len(topField) == 0:
            topField = fieldList[-1]
            topAge = int(topField[-14:-11])
            arcpy.AlterField_management(estMem,topField[:-7]+"BT_2010",topField[:-11]+"PLUSBT_2010")
            arcpy.AlterField_management(estMem,topField[:-7]+"FT_2010",topField[:-11]+"PLUSFT_2010")
            arcpy.AlterField_management(estMem,topField[:-7]+"MT_2010",topField[:-11]+"PLUSMT_2010")
        else:
            topAge = int(topField[0][-14:-11])

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

        #calculate broad age categories, women of childbearing age
        with arcpy.da.UpdateCursor(estMem,["E_A000_014BT_2010","E_A000_004BT_2010","E_A005_009BT_2010","E_A010_014BT_2010",
                                           "E_A015_049FT_2010","E_A015_019FT_2010","E_A020_024FT_2010","E_A025_029FT_2010",
                                           "E_A030_034FT_2010","E_A035_039FT_2010","E_A040_044FT_2010","E_A045_049FT_2010",
                                           "E_A015_064BT_2010","E_A015_019BT_2010","E_A020_024BT_2010","E_A025_029BT_2010",
                                           "E_A030_034BT_2010","E_A035_039BT_2010","E_A040_044BT_2010","E_A045_049BT_2010",
                                           "E_A050_054BT_2010","E_A055_059BT_2010","E_A060_064BT_2010"],"E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
            for row in cursor:
                row[0] = row[1]+row[2]+row[3]
                row[4] = sum(row[5:12])
                row[12] = sum(row[13:])
                
                cursor.updateRow(row)

        print iso+": other"
        arcpy.CopyRows_management(estMem,estTable+"_reprocessed")


print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
