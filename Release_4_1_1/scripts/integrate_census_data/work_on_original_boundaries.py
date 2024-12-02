import arcpy, os
arcpy.env.overwriteOutput = True

root = r'\\dataserver1\gpw\GPW4\Release_411\data\boundaries'
#root = r'D:\GPW'
origFolder = os.path.join(root,'original_boundaries_with_census_data')
adjFolder = os.path.join(root,'adjusted_boundaries_with_census_data')
outGDB = os.path.join(root,'original_boundaries_admin0','admin0.gdb')

arcpy.env.workspace = origFolder
gdbList = arcpy.ListWorkspaces()
gdbList.sort()

gdb = gdbList[9]
for gdb in gdbList:
    iso = os.path.basename(gdb)[:-4]
    print(iso)
    
    arcpy.env.workspace = gdb
    fcList = arcpy.ListFeatureClasses()
    if len(fcList) > 1:
        continue
    
    origFC = fcList[0]
    
    adjFC = origFC + "_adj"
    origPoint = origFC + "_point"
    adjPoint = origFC + "_point_adj"
    
    arcpy.FeatureClassToFeatureClass_conversion(os.path.join(adjFolder, iso+".gdb", origFC),gdb,adjFC)
    
    fList = [f.name for f in arcpy.ListFields(adjFC) if not f.required and not f.name == 'UBID']
    if len(fList) > 0:
        arcpy.DeleteField_management(adjFC, fList)

    arcpy.FeatureToPoint_management(origFC, origPoint, "INSIDE")
    arcpy.FeatureToPoint_management(adjFC, adjPoint, "INSIDE")
    
    joinFC1 = origFC + "_orig_join_adj"
    joinFC2 = origFC + "_adj_join_orig"
    
    arcpy.SpatialJoin_analysis(origPoint, adjFC, joinFC1)
    arcpy.SpatialJoin_analysis(adjPoint, origFC, joinFC2)
    
    fList = [f.name for f in arcpy.ListFields(joinFC1) if not f.required and not f.name in ['TEMPID','UBID']]
    if len(fList) > 0:
        arcpy.DeleteField_management(joinFC1, fList)
    fList = [f.name for f in arcpy.ListFields(joinFC2) if not f.required and not f.name in ['TEMPID','UBID']]
    if len(fList) > 0:
        arcpy.DeleteField_management(joinFC2, fList)
        
    arcpy.AddField_management(origFC,'UBID',"TEXT","","",100)
    arcpy.AddField_management(origFC,'edit',"TEXT","","",100)
    
    # Find units that should be merged
    d = {}
    ubids = {}
    with arcpy.da.SearchCursor(joinFC1, ['TEMPID','UBID'], "UBID IS NOT NULL") as cursor:
        for row in cursor:
            d[row[0]] = row[1]
            if row[1] in ubids:
                ubids[row[1]] += 1
            else:
                ubids[row[1]] = 1
                    
    with arcpy.da.UpdateCursor(origFC, ['TEMPID','UBID','edit']) as cursor:
        for row in cursor:
            if row[0] in d:
                row[1] = d[row[0]]
                count = ubids[row[1]]
                if count > 1:
                    row[2] = 'Merge'
            else:
                row[2] = 'No UBID'
            cursor.updateRow(row)
            
    # Find units that should be split
    tempids = {}
    with arcpy.da.SearchCursor(joinFC2, 'TEMPID',"TEMPID IS NOT NULL") as cursor:
        for row in cursor:
            if row[0] in tempids:
                tempids[row[0]] += 1
            else:
                tempids[row[0]] = 1
    
    with arcpy.da.UpdateCursor(origFC, ['TEMPID','edit']) as cursor:
        for row in cursor:
            if row[0] in tempids:
                if tempids[row[0]] > 1:
                    if row[1] == None:
                        row[1] = "Split"
                    else:
                        row[1] = row[1]+", Split"
            else:
                if row[1] == None:
                    row[1] = "No adj unit inside"
                else:
                    row[1] = row[1]+", No adj unit inside"
            cursor.updateRow(row)
    
    # How many units need editing
    count = 0
    with arcpy.da.SearchCursor(origFC,'edit',"edit IS NOT NULL") as cursor:
        for row in cursor:
            count += 1
    
    if count > 0:
        print("  {} units need editing".format(count))
        
    arcpy.Delete_management(joinFC1)
    arcpy.Delete_management(joinFC2)
    arcpy.Delete_management(origPoint)
    arcpy.Delete_management(adjPoint)

# check join
gdb = gdbList[-1]
for gdb in gdbList[69:]:
    iso = os.path.basename(gdb)[:-4]
    
    print(iso)
    
    arcpy.env.workspace = gdb
    fcList = arcpy.ListFeatureClasses()
    fcList.sort()
    
    fcOrig = fcList[0]
    fcAdj = fcList[1]
    
    adjIDs = [row[0] for row in arcpy.da.SearchCursor(fcAdj,"UBID")]
    
    countNulls = 0
    dups = []
    origIDs = []
    with arcpy.da.SearchCursor(fcOrig,"UBID") as cursor:
        for row in cursor:
            if row[0] is None:
                countNulls += 1
            else:
                if row[0] in origIDs:
                    dups.append(row[0])
                else:
                    origIDs.append(row[0])
    
    if countNulls > 0:
        print("  {} null values".format(countNulls))
    if len(dups) > 0:
        print("  {} duplicates: {}".format(len(dups), dups))
    
    missingFromOrig = []
    missingFromAdj = []
    
    for i in adjIDs:
        if i not in origIDs:
            missingFromOrig.append(i)
            
    for i in origIDs:
        if i not in adjIDs:
            missingFromAdj.append(i)
    
    if len(missingFromOrig) > 0:
        print ("  {} units missing from original: {}".format(len(missingFromOrig),missingFromOrig))
    
    if len(missingFromAdj) > 0:
        print ("  {} units missing from adjusted: {}".format(len(missingFromAdj),missingFromAdj))

gdb = gdbList[0]
for gdb in gdbList[1:]:
    iso = os.path.basename(gdb)[:-4]
    
    print(iso)
    
    arcpy.env.workspace = gdb
    fcList = arcpy.ListFeatureClasses("*adj")
    
    for fc in fcList:
        arcpy.Delete_management(fc)
    
    fcList = arcpy.ListFeatureClasses()
    for fc in fcList:
        fList = [f.name for f in arcpy.ListFields(fc) if not f.required and not f.name == 'UBID']
        if len(fList) > 0:
            arcpy.DeleteField_management(fc,fList)

gdb = gdbList[0]
for gdb in gdbList[1:]:
    iso = os.path.basename(gdb)[:-4]
    
    print(iso)
    
    arcpy.env.workspace = gdb
    fcList = arcpy.ListFeatureClasses()

    featData = os.path.join(gdb,iso+'_topology')
    gdbTopo = os.path.join(featData,'topology')
    arcpy.CreateFeatureDataset_management(gdb,iso+'_topology',arcpy.Describe(fcList[0]).spatialReference)
    arcpy.CreateTopology_management(featData,'topology')
    
    fc = fcList[0]    
    for fc in fcList:
        topoFC = os.path.join(featData,fc.replace("_boundaries",""))
        arcpy.CopyFeatures_management(fc,topoFC)
        arcpy.AddFeatureClassToTopology_management(gdbTopo,topoFC)
        arcpy.AddRuleToTopology_management(gdbTopo,'Must Not Overlap (Area)',topoFC)
        arcpy.ValidateTopology_management(gdbTopo)

gdb = gdbList[9]
for gdb in gdbList[9:]:
    iso = os.path.basename(gdb)[:-4]
    
    print(iso)
    
    arcpy.env.workspace = gdb
    fcList = arcpy.ListFeatureClasses()
    for fc in fcList:
        arcpy.Delete_management(fc)
    
    featData = os.path.join(gdb,iso+'_topology')
    arcpy.env.workspace = featData
    fcList = arcpy.ListFeatureClasses()
    for fc in fcList:
        arcpy.FeatureClassToFeatureClass_conversion(fc,gdb,fc+"_boundaries")
    
    arcpy.Delete_management(featData)

gdb = gdbList[0]
for gdb in gdbList[4:]:
    iso = os.path.basename(gdb)[:-4]
    print(iso)
    
    arcpy.env.workspace = gdb
    fcList = arcpy.ListFeatureClasses()
    fcList.sort()
    fc = fcList[0]
    for fc in fcList:
        dissFC = os.path.join(outGDB,fc.replace("_boundaries","_dissolve"))
        arcpy.Dissolve_management(fc,dissFC)
        unionFC = os.path.join(outGDB,fc.replace("_boundaries","_union"))
        arcpy.Union_analysis(dissFC, unionFC, "NO_FID", "", "NO_GAPS")
        maxArea = 0
        units = 0
        with arcpy.da.SearchCursor(unionFC,"SHAPE_Area") as cursor:
            for row in cursor:
                units += 1
                if row[0] > maxArea:
                    maxArea = row[0]
        if units > 1:
            with arcpy.da.UpdateCursor(unionFC,"SHAPE_Area") as cursor:
                for row in cursor:
                    if row[0] == maxArea:
                        cursor.deleteRow()
            singleFC = os.path.join(outGDB,fc.replace("_boundaries","_singlepart"))
            arcpy.MultipartToSinglepart_management(unionFC,singleFC)
        arcpy.Delete_management(dissFC)
        arcpy.Delete_management(unionFC)

arcpy.env.workspace = outGDB
fcList = arcpy.ListFeatureClasses()
fcList.sort()
fc = fcList[0]
for fc in fcList:
    iso = fc[:3]
    print(iso)
    
    origFC = os.path.join(origFolder, iso+".gdb", fc.replace("_singlepart","_boundaries"))
    
    arcpy.Append_management(fc,origFC,"NO_TEST")
    arcpy.MakeFeatureLayer_management(fc,iso+"_lyr")
    arcpy.SelectLayerByAttribute_management(iso+"_lyr", "NEW_SELECTION", "UBID IS NULL")
    
    elimFC = os.path.join(origFolder, iso+".gdb", fc.replace("_singlepart","_eliminate"))
    arcpy.Eliminate_management(iso+"_lyr",elimFC)
    
    arcpy.MakeFeatureLayer_management(elimFC,iso+"_elim")
    arcpy.SelectLayerByAttribute_management(iso+"_elim","NEW_SELECTION","UBID IS NULL")
    count = int(arcpy.GetCount_management(iso+"_elim").getOutput(0))
    if count > 0:
        print("  {} units with no UBID".format(count))
    
for gdb in gdbList:
    iso = os.path.basename(gdb)[:-4]
    
    arcpy.env.workspace = gdb
    fcList = arcpy.ListFeatureClasses("*eliminate")
    
    if len(fcList) > 0:
        print(iso)
        if len(fcList) > 1:
            print("  too many feature classes")
        else:
            fc = fcList[0]
            origFC = fc.replace("_eliminate","")
            arcpy.Delete_management(origFC)
            arcpy.Rename_management(fc,origFC)

    

