import arcpy, os
dataFolder = r'D:\gpw\release_4_1\loading\processed'
boundaries = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\working'

#isos = ['kaz']
isos = ['aus','bra','can','chn','grl','ind','rus']

for iso in isos:
    print iso
    inGDB = os.path.join(dataFolder,iso+'.gdb')
    arcpy.env.workspace = inGDB
    arcpy.env.overwriteOutput = True

    table = arcpy.ListTables("*estimates")[0]
    memTable = 'in_memory' + os.sep + table
    arcpy.CopyRows_management(table,memTable)
    arcpy.AddField_management(memTable,"tile","TEXT","","",50)

    boundGDB = os.path.join(boundaries,iso+'.gdb')
    arcpy.env.workspace = boundGDB
    fc = arcpy.ListFeatureClasses("*2010")[0]

    tileDict = {}
    tileList = []

    with arcpy.da.SearchCursor(fc,['UBID','tile']) as cursor:
        for row in cursor:
            tileDict[row[0]] = row[1]
            if not row[1] in tileList:
                tileList.append(row[1])

    with arcpy.da.UpdateCursor(memTable,["UBID","tile"]) as cursor:
        for row in cursor:
            if row[0] in tileDict:
                row[1] = tileDict[row[0]]
            else:
                print row[0], "not found"
            cursor.updateRow(row)

    tileList.sort()
    for tile in tileList:
        print tile
        outGDB = os.path.join(dataFolder,iso+'_'+tile+'.gdb')
        arcpy.CreateFileGDB_management(dataFolder,iso+'_'+tile+'.gdb')
        arcpy.TableToTable_conversion(memTable,outGDB,iso+"_"+tile+table[3:],"tile = '"+tile+"'")
        arcpy.DeleteField_management(os.path.join(outGDB,iso+"_"+tile+table[3:]),'tile')

    del memTable
    del tileDict


print "done"

