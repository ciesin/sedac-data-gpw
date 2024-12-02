# Jane Mills
# 12/9/2020
# GPW
# join census data to gridding boundaries

import arcpy, os
arcpy.env.overwriteOutput = True

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
    fcList = arcpy.ListFeatureClasses("*growth_rate*")
    
    if len(fcList) != 1:
        print("  Did not find the right number of feature classes")
        with open(errors, "a") as f:
            f.write(iso+": no growth rate feature class\n")
        continue
    
    arcpy.env.workspace = tableGDB
    tableList = arcpy.ListTables("*growth_rate*")
    allTables = arcpy.ListTables()
    
    if len(tableList) != 1:
        print("  Did not find the right number of growth rate tables")
        with open(errors, "a") as f:
            f.write(iso+": no growth rate table\n")
        continue
    
    fc = fcList[0]
    fcPath = os.path.join(boundaryGDB, fc)
    level = fc.split("_")[3]
    print(iso+" "+level)
    
    inTable = os.path.join(tableGDB, tableList[0])
    
    fieldList = ['agrid','agrid_source','gr_start_pop','gr_end_pop','gr_start_year','gr_end_year']
    inFields = [f.name for f in arcpy.ListFields(inTable)]
    missing = [f for f in fieldList if f not in inFields]
    if len(missing) > 0:
        print("  Didn't find field: {} in growth rate table".format(f))
        with open(errors, "a") as f:
            f.write(iso+" "+level+": growth rate table missing fields\n")
        continue
    grDict = {}
    sources = []
    with arcpy.da.SearchCursor(inTable,fieldList) as cursor:
        for row in cursor:
            grDict[str(row[0])] = list(row[2:])
            if row[1] not in sources:
                sources.append(row[1])
    
    if len(sources) > 1:
        print("  You might need to address this manually")
        with open(errors, "a") as f:
            f.write(iso+" "+level+": multiple growth rate levels\n")
        continue
    sources = sources[0]
    
    # change USCID to UBID
    if sources == 'USCID':
        tempDict = grDict
        grDict = {}
        estTable = [t for t in allTables if level in t and t[-9:] == "estimates"]
        
        if len(estTable) != 1:
            print("  Can't translate USCID to UBID")
            with open(errors, "a") as f:
                f.write(iso+" "+level+": can't translate USCID to UBID\n")
            continue
        estTable = estTable[0]
        with arcpy.da.SearchCursor(estTable,["USCID","UBID"]) as cursor:
            for row in cursor:
                if str(row[0]) in tempDict:
                    grDict[str(row[1])] = tempDict[row[0]]
        sources = 'UBID'
    
    # get list of fields we need to join
    sourceFields = sources.split("_")
    
    # join
    arcpy.AddField_management(fcPath,"GSTARTPOP","DOUBLE")
    arcpy.AddField_management(fcPath,"GENDPOP","DOUBLE")
    arcpy.AddField_management(fcPath,"GSTARTYEAR","SHORT")
    arcpy.AddField_management(fcPath,"GENDYEAR","SHORT")
    
    count = 0
    nullcount = 0
    with arcpy.da.UpdateCursor(fcPath,sourceFields+["GSTARTPOP","GENDPOP","GSTARTYEAR","GENDYEAR"]) as cursor:
        for row in cursor:
            if "UCADMIN0" in sourceFields:
                rid = row[:len(sourceFields)]
                rid[0] = str(int(rid[0]))
                rid = "_".join(rid)
            else:
                rid = "_".join(row[:len(sourceFields)])
            if rid in grDict:
                row[-4:] = grDict[rid]
                if None in grDict[rid]:
                    nullcount += 1
                cursor.updateRow(row)
            else:
                count += 1
    
    if count > 0:
        print("  {} rows did not get growth rate info".format(count))
        with open(errors, "a") as f:
            f.write(iso+" "+level+": {} rows with no growth rate data\n".format(count))
    
    if nullcount > 0:
        print("  {} rows have some missing data".format(nullcount))
        with open(errors, "a") as f:
            f.write(iso+" "+level+": {} rows with some missing growth rate data\n".format(nullcount))


