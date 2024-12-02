#Jane Mills
#5/12/17
#GPWv4
#Apply age/sex proportions (assume 2010 sex has already been calculated)

import arcpy, os, numpy

arcpy.env.overwriteOutput = True

#change paths to scale
inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\jane_testing_proportions\irn.gdb'
iso = os.path.basename(inGDB)[:-4]
agetable = os.path.join(inGDB,'irn_admin0_2011_age_sex_group')
propTable = agetable + "_proportions"
estTable = os.path.join(inGDB,'irn_admin2_2011_estimates')

#find admin level of age x sex data, total pop data
ageLevel = 0
popLevel = 2

#build a dictionary with high level USCID as keys, low level USCID as values
if ageLevel < popLevel:
    raw = os.path.join(inGDB,'irn_admin0_2011_raw')
    lookup = os.path.join(inGDB,'irn_admin2_2011_lookup')

    LLDict = {}
    fList = [f.name for f in arcpy.ListFields(raw,"UCADMIN*")]
    fList.sort()
    fList.insert(0,"USCID")
    with arcpy.da.SearchCursor(raw,fList) as cursor:
        for row in cursor:
            admins = '_'.join(str(x) for x in row[1:])
            LLDict[admins] = row[0]

    USCIDs = {}
    with arcpy.da.SearchCursor(lookup,fList) as cursor:
        for row in cursor:
            admins = '_'.join(str(x) for x in row[1:])
            lowUSCID = LLDict[admins]
            USCIDs[row[0]] = lowUSCID
    del LLDict

memTable = 'in_memory' + os.sep + iso
arcpy.CopyRows_management(estTable,memTable)

#Add age BT fields
totalFields = [f.name for f in arcpy.ListFields(propTable,"A*FT_PROP")]
for f in totalFields:
    arcpy.AddField_management(memTable,"E_"+f[:-7]+"BT_2010","DOUBLE")

#loop through female and male
for sex in ['F','M']:
    sexFields = [f.name for f in arcpy.ListFields(propTable,"A*"+sex+"T_PROP")]
    for f in sexFields:
        arcpy.AddField_management(memTable,"E_"+f[:-5]+"_2010","DOUBLE")

    #leave out anr and any null fields when updating
    fieldList = []
    for f in sexFields:
        with arcpy.da.SearchCursor(propTable,f,'OBJECTID = 1') as cursor:
            for row in cursor:
                if not row[0] is None and not f in fieldList:
                    fieldList.append(f)

    #build dictionary of proportions
    fieldList.sort()
    searchFields = ["USCID"] + fieldList
    updateFields = ["E_"+f[:-5]+"_2010" for f in fieldList] + ["E_ATOTPOP"+sex+"T_2010"] + ["USCID"]

    propDict = {}
    with arcpy.da.SearchCursor(propTable,searchFields) as cursor:
        for row in cursor:
            propDict[row[0]] = row[1:]

    #apply proportions
    with arcpy.da.UpdateCursor(memTable,updateFields) as cursor:
        for row in cursor:
            uscid = row[-1]
            #find the lower level USCID and those proportions (if necessary)
            if ageLevel < popLevel:
                lluscid = USCIDs[uscid]
                props = propDict[lluscid]
            else:
                props = propDict[uscid]
            total = row[-2]
            for i in range(len(updateFields)-2):
                row[i] = props[i]*total
            cursor.updateRow(row)

#calculate BT ages
finalFields = ["E_"+f[:-7]+"BT_2010" for f in fieldList] + ["E_"+f[:-7]+"FT_2010" for f in fieldList] + ["E_"+f[:-7]+"MT_2010" for f in fieldList]
with arcpy.da.UpdateCursor(memTable,finalFields) as cursor:
    for row in cursor:
        row[:len(finalFields)/3] = list(numpy.add(row[len(finalFields)/3:-len(finalFields)/3],row[-len(finalFields)/3:]))
        cursor.updateRow(row)

arcpy.Delete_management(estTable)
arcpy.CopyRows_management(memTable,estTable)

#Now you can calculate the PLUS categories
