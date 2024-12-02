#Jane Mills
#5/12/17
#GPWv4
#Calculate age/sex proportions

import arcpy, os

#change paths to scale
inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\jane_testing_proportions\usadc.gdb'
agetable = os.path.join(inGDB,'usadc_admin5_2010_age_sex_group')
propTable = os.path.join(inGDB,'usadc_admin5_2010_age_sex_group_proportions')

memTable = 'in_memory' + os.sep + iso

arcpy.CopyRows_management(agetable,memTable)

for sex in ['F','M']:
    sexFields = [f.name for f in arcpy.ListFields(memTable,"A*"+sex+"T")]
    for f in sexFields:
        if not "ANR" in f:
            arcpy.AddField_management(memTable,f+"_PROP","DOUBLE")

    #leave out anr and any fields without age categories
    fieldList = []
    for f in sexFields:
        if not "ANR" in f:
            with arcpy.da.SearchCursor(memTable,f,'OBJECTID = 1') as cursor:
                for row in cursor:
                    if not row[0] is None and not f in fieldList:
                        fieldList.append(f)                    

    fieldList.sort()
    searchFields = fieldList + [f+"_PROP" for f in fieldList]

    #Calculate proportions
    with arcpy.da.UpdateCursor(memTable,searchFields) as cursor:
        for row in cursor:
            total = sum(row[:len(searchFields)/2])
            for i in range(len(searchFields)/2,len(searchFields)):
                if total > 0:
                    row[i] = row[i-len(searchFields)/2]/total
                else:
                    row[i] = 0
            cursor.updateRow(row)

arcpy.CopyRows_management(memTable,propTable)



