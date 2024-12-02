# Jane Mills
# 12/9/2020
# GPW
# join census data to gridding boundaries

import arcpy, os

tableFolder = r'\\dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\global\tables\processed_pop_tables'
boundsFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\adjusted_boundaries_with_census_data'
errors = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\error_messages.txt'

boundaryGDBs = [os.path.join(boundsFolder,b) for b in os.listdir(boundsFolder) if b[-4:] == '.gdb']
boundaryGDBs.sort()

boundaryGDB = boundaryGDBs[114]
for boundaryGDB in boundaryGDBs:
    iso = os.path.basename(boundaryGDB)[:-4]
    
    tableGDB = os.path.join(tableFolder,iso+".gdb")
    
    if not os.path.exists(tableGDB):
        print("  Can't find table GDB")
        with open(errors, "a") as f:
            f.write(iso+": no table GDB\n")
        continue
    
    arcpy.env.workspace = boundaryGDB
    fcList = arcpy.ListFeatureClasses()
    fcList.sort()
    
    arcpy.env.workspace = tableGDB
    tableList = arcpy.ListTables()
    
    #fc = fcList[2]
    for fc in fcList:
        fcPath = os.path.join(boundaryGDB, fc)
        level = fc.split("_")[1]
        print(iso+" "+level)
        
        inTables = [t for t in tableList if level in t and "_raw" in t]
        inTables.sort()
    
        if len(inTables) == 0:
            print("  Didn't find any tables")
            with open(errors, "a") as f:
                f.write(iso+" "+level+": no tables in the GDB\n")
            continue
        
        #t = inTables[0]
        for t in inTables:
            inTable = os.path.join(tableGDB, t)
            
            # join raw data to boundaries based on UCADMIN codes
            fieldList = [f.name for f in arcpy.ListFields(inTable, "CENSUS*YEAR")] + [f.name for f in arcpy.ListFields(inTable,"A*")]
            idFields = ["UCADMIN"+str(i) for i in range(int(level[-1])+1)]
            tableDict = {}
            with arcpy.da.SearchCursor(inTable,idFields+fieldList) as cursor:
                for row in cursor:
                    rid = "_".join([str(int(i)) for i in row[:len(idFields)]])
                    tableDict[rid] = list(row[len(idFields):])
                    
            for f in fieldList:
                if "CENSUS" in f:
                    arcpy.AddField_management(fcPath,"CENSUSYEAR","SHORT")
                    fieldList[0] = "CENSUSYEAR"
                else:
                    arcpy.AddField_management(fcPath,f,"DOUBLE")
                    
            count = 0
            with arcpy.da.UpdateCursor(fcPath,idFields+fieldList+['CONTEXT','WATER_CODE']) as cursor:
                for row in cursor:
                    rid = row[:len(idFields)]
                    rid[0] = str(int(rid[0]))
                    rid = "_".join(rid)
                    if rid in tableDict:
                        row[len(idFields):-2] = tableDict[rid]
                        cursor.updateRow(row)
                    else:
                        if row[-2] == 204 or row[-2] == 205 or row[-1] == 'IW':
                            row[len(idFields)+1:-2] = [0]*len(fieldList)
                            cursor.updateRow(row)
                        if row[-2] == 0 and row[-1] == 'L':
                            count += 1
                        
            if count > 0:
                print("  {} rows with no census data".format(count))
                with open(errors, "a") as f:
                    f.write(iso+" "+level+": {} rows with no census data\n".format(count))

