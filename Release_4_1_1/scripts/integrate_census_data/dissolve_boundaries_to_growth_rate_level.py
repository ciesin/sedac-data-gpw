# Jane Mills
# 12/8/2020
# GPW
# dissolve boundaries to all levels of input data

import arcpy, os
arcpy.env.overwriteOutput = True

tableFolder = r'\\dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\global\tables\processed_pop_tables'
inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\adjusted_boundaries_with_census_data'

boundaryGDBs = [os.path.join(inFolder,b) for b in os.listdir(inFolder) if b[-4:] == '.gdb']
boundaryGDBs.sort()

boundaryGDB = boundaryGDBs[114]
for boundaryGDB in boundaryGDBs[1:]:
    iso = os.path.basename(boundaryGDB)[:-4]
    print(iso)
    
    tableGDB = os.path.join(tableFolder,iso+".gdb")
    
    if not os.path.exists(tableGDB):
        print("Can't find table GDB")
        continue
    
    arcpy.env.workspace = boundaryGDB
    fcList = arcpy.ListFeatureClasses()
    fcList.sort()
    
    levels = [fc.split("_")[1] for fc in fcList]
    
    arcpy.env.workspace = tableGDB
    grTables = arcpy.ListTables("*growth_rate*")
    
    if not len(grTables) == 1:
        print("Didn't find the right number of growth rate tables")
        continue
    
    grTable = grTables[0]
    grlevel = grTable.split("_")[3]
    
    outFC = os.path.join(boundaryGDB, iso+"_growth_rate_"+grlevel+"_boundaries")
    if grlevel not in levels:
        fcPath = os.path.join(boundaryGDB,fcList[-1])
        levelnum = int(grlevel[-1])
        
        dissFields = ['ISOALPHA']+['UCADMIN'+str(l) for l in range(levelnum+1)]+['NAME'+str(l) for l in range(levelnum+1)]
        arcpy.Dissolve_management(fcPath, outFC, dissFields)
        
        for i in range(levelnum+1,7):
            arcpy.AddField_management(outFC,"UCADMIN"+str(i),"TEXT","","",50)
            arcpy.AddField_management(outFC,"NAME"+str(i),"TEXT","","",100)
        
        arcpy.AddField_management(outFC,'CONTEXT','SHORT')
        arcpy.AddField_management(outFC,'CONTEXT_NM','TEXT',"","",100)
        arcpy.AddField_management(outFC,'WATER_CODE','TEXT',"","",2)
        
        count = 0
        uFields = ['NAME'+grlevel[-1],'CONTEXT','CONTEXT_NM','WATER_CODE'] + ['UCADMIN'+str(i) for i in range(levelnum+1,7)] + ['NAME'+str(i) for i in range(levelnum+1,7)]
        with arcpy.da.UpdateCursor(outFC,uFields) as cursor:
            for row in cursor:
                if row[0] == 'NA':
                    count += 1
                    cursor.deleteRow()
                else:
                    row[1] = 0
                    row[2] = 'Not applicable'
                    row[3] = 'L'
                    row[4:] = ['NA']*len(row[4:])
                    cursor.updateRow(row)
        
        if count > 0:
            arcpy.MakeFeatureLayer_management(fcPath,'NAs',"NAME"+grlevel[-1]+" = 'NA'")
            
            result = arcpy.GetCount_management('NAs')[0]
            print("  Adding {} NA features".format(result))
            
            arcpy.Append_management('NAs',outFC,'NO_TEST')
            
    else:
        fcPath = os.path.join(boundaryGDB,iso+"_"+grlevel+"_boundaries")
        arcpy.CopyFeatures_management(fcPath,outFC)
        fList = [f.name for f in arcpy.ListFields(outFC,"A*")] + [f.name for f in arcpy.ListFields(outFC,"CENSUSYEAR")]
        if len(fList) > 0:
            arcpy.DeleteField_management(outFC,fList)

