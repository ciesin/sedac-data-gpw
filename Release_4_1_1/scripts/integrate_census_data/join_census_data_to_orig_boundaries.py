import arcpy, os
arcpy.env.overwriteOutput = True

root = r'\\dataserver1\gpw\GPW4\Release_411\data\boundaries'
origFolder = os.path.join(root,'original_boundaries_with_census_data')
adjFolder = os.path.join(root,'adjusted_boundaries_with_census_data')

arcpy.env.workspace = origFolder
gdbList = arcpy.ListWorkspaces()
gdbList.sort()

#gdb = gdbList[0]
for gdb in gdbList[36:]:
    iso = os.path.basename(gdb)[:-4]
    print(iso)
    
    arcpy.env.workspace = gdb
    fcList = arcpy.ListFeatureClasses()
    fcList.sort()
    
    # high level census data
    if len(fcList) > 1:
        jField = "UCADMIN3"
    else:
        jField = "UBID"
    
    fc = fcList[0]
    for fc in fcList:
        adjFC = os.path.join(adjFolder, iso+".gdb", fc)
        
        fList = [f for f in arcpy.ListFields(adjFC) if not f.required and not f.name == 'UBID']
        
        for f in fList:
            if f.type == 'String':
                arcpy.AddField_management(fc, f.name, f.type, "", "", f.length)
            else:
                arcpy.AddField_management(fc, f.name, f.type)
                
        fList = [f.name for f in fList]
        
        d = {}
        with arcpy.da.SearchCursor(adjFC,[jField]+fList) as cursor:
            for row in cursor:
                d[row[0]] = row[1:]
        
        count = 0
        with arcpy.da.UpdateCursor(fc,["UBID"]+fList) as cursor:
            for row in cursor:
                if row[0] in d:
                    row[1:] = d[row[0]]
                    cursor.updateRow(row)
                else:
                    count += 1
        
        if count > 0:
            print("  {} units did not get data".format(count))
            
    # growth rates
    origFC = os.path.join(gdb,fcList[0])
    
    arcpy.env.workspace = os.path.join(adjFolder, iso+".gdb")
    grAdjFC = arcpy.ListFeatureClasses("*growth*")[0]
    grLevel = grAdjFC.split("_")[3]
    levelnum = int(grLevel[-1])
    
    outFC = os.path.join(gdb, iso+"_growth_rate_"+grLevel+"_boundaries")
    
    arcpy.Dissolve_management(origFC, outFC, 'GRID')
    
    fList = [f for f in arcpy.ListFields(grAdjFC) if not f.required and not f.name == 'GRID']
    for f in fList:
        if f.type == 'String':
            arcpy.AddField_management(outFC, f.name, f.type, "", "", f.length)
        else:
            arcpy.AddField_management(outFC, f.name, f.type)
    fList = [f.name for f in fList]
    
    d = {}
    with arcpy.da.SearchCursor(grAdjFC,['GRID']+fList) as cursor:
        for row in cursor:
            d[row[0]] = row[1:]
    
    count = 0
    with arcpy.da.UpdateCursor(outFC,["GRID"]+fList) as cursor:
        for row in cursor:
            if row[0] in d:
                row[1:] = d[row[0]]
                cursor.updateRow(row)
            else:
                count += 1
    
    if count > 0:
        print("  {} units did not get growth rate data".format(count))
        
    #lower level boundaries
    dissList = [f for f in arcpy.ListFeatureClasses() if not "growth" in f and not f in fcList]
    for fc in dissList:
        outFC = os.path.join(gdb,fc)
        levelnum = int(fc.split("_")[1][-1])
        dissFields = ['ISOALPHA']+['UCADMIN'+str(l) for l in range(levelnum+1)]+['NAME'+str(l) for l in range(levelnum+1)]
        arcpy.Dissolve_management(origFC, outFC, dissFields)
        
        fList = [f for f in arcpy.ListFields(fc) if not f.required and not f.name in dissFields]
        for f in fList:
            if f.type == 'String':
                arcpy.AddField_management(outFC, f.name, f.type, "", "", f.length)
            else:
                arcpy.AddField_management(outFC, f.name, f.type)
        fList = [f.name for f in fList]
        
        d = {}
        idFields = ['UCADMIN'+str(l) for l in range(levelnum+1)]
        with arcpy.da.SearchCursor(fc,idFields+fList) as cursor:
            for row in cursor:
                rid = "_".join(row[:len(idFields)])
                d[rid] = row[len(idFields):]
        
        count = 0
        with arcpy.da.UpdateCursor(outFC,idFields+fList) as cursor:
            for row in cursor:
                rid = "_".join(row[:len(idFields)])
                if rid in d:
                    row[len(idFields):] = d[rid]
                    cursor.updateRow(row)
                else:
                    count += 1
        
        if count > 0:
            print("  {} units did not get lower level data".format(count))

