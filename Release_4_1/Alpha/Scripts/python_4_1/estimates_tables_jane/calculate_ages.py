#Jane Mills
#5/12/17
#GPWv4
#Apply age/sex proportions (assume 2010 sex has already been calculated)

import arcpy, os, numpy

arcpy.env.overwriteOutput = True

#change paths to scale
inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\jane_testing_proportions\usadc.gdb'
iso = os.path.basename(inGDB)[:-4]
estTable = os.path.join(inGDB,'usadc_admin5_2010_estimates')

#Add BT age fields
fieldList  = []
fields = arcpy.ListFields(estTable,"E_A*FT_2010")
for f in fields:
    if not "TOTPOP" in f.name:
        fieldList.append(f.name)
        arcpy.AddField_management(estTable,f.name[:-7]+"BT_2010","DOUBLE")

print "added BT categories"

#calculate ages
fieldList.sort()
finalFields = [f[:-7]+"BT_2010" for f in fieldList] + [f[:-7]+"FT_2010" for f in fieldList] + [f[:-7]+"MT_2010" for f in fieldList]
with arcpy.da.UpdateCursor(estTable,finalFields) as cursor:
    for row in cursor:
        row[:len(finalFields)/3] = list(numpy.add(row[len(finalFields)/3:-len(finalFields)/3],row[-len(finalFields)/3:]))
        cursor.updateRow(row)

print "calculated BT categories"

#calculate PLUS categories
topField = [f.name for f in arcpy.ListFields(estTable,"E_A*PLUSBT_2010")]
topAge = int(topField[0][-14:-11])

if topAge > 65:
    for i in reversed(range(65,topAge,5)):
        age = str(i).zfill(3)
        top = str(i+4).zfill(3)
        nextAge = str(i+5).zfill(3)

        ageFields = ["E_A"+age+"PLUSBT_2010","E_A"+age+"PLUSFT_2010","E_A"+age+"PLUSMT_2010",
                     "E_A"+age+"_"+top+"BT_2010","E_A"+age+"_"+top+"FT_2010","E_A"+age+"_"+top+"MT_2010",
                     "E_A"+nextAge+"PLUSBT_2010","E_A"+nextAge+"PLUSFT_2010","E_A"+nextAge+"PLUSMT_2010"]

        arcpy.AddField_management(estTable,ageFields[0],"DOUBLE")
        arcpy.AddField_management(estTable,ageFields[1],"DOUBLE")
        arcpy.AddField_management(estTable,ageFields[2],"DOUBLE")

        with arcpy.da.UpdateCursor(estTable,ageFields) as cursor:
            for row in cursor:
                row[0] = row[3]+row[6]
                row[1] = row[4]+row[7]
                row[2] = row[5]+row[8]
                cursor.updateRow(row)

print "calculated plus categories"

#calculate broad age categories, women of childbearing age
arcpy.AddField_management(estTable,"E_A000_014BT_2010","DOUBLE")
arcpy.AddField_management(estTable,"E_A015_064BT_2010","DOUBLE")
arcpy.AddField_management(estTable,"E_A015_049FT_2010","DOUBLE")

with arcpy.da.UpdateCursor(estTable,["E_A000_014BT_2010","E_A000_004BT_2010","E_A005_009BT_2010","E_A010_014BT_2010",
                                     "E_A015_064BT_2010","E_ATOTPOPBT_2010","E_A065PLUSBT_2010",
                                     "E_A015_049FT_2010","E_A015_019FT_2010","E_A020_024FT_2010","E_A025_029FT_2010",
                                     "E_A030_034FT_2010","E_A035_039FT_2010","E_A040_044FT_2010","E_A045_049FT_2010"]) as cursor:
    for row in cursor:
        row[0] = row[1]+row[2]+row[3]
        row[4] = row[5]-row[0]-row[6]
        row[7] = sum(row[8:])
        cursor.updateRow(row)

print "calculated other categories"
