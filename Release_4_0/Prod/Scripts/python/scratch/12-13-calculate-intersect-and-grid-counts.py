# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing

def calculateIntersectCounts(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-4]
    try:
        arcpy.env.workspace = gdb
        # grab estimatesFile
        estimatesFile = gdb + os.sep + arcpy.ListTables("*estimates")[0]
        # grab intersected fishnet
        fishGDB = gdb.replace("pop_tables","fishnets").replace(".gdb","_fishnet.gdb")
        arcpy.env.workspace = fishGDB
        intersectedFishnet = arcpy.ListFeatureClasses("*_intersect")[0]
        # read the files into memory
        memFishnet = 'in_memory' + os.sep + os.path.basename(intersectedFishnet) + "_view"
        try:
            arcpy.CopyRows_management(intersectedFishnet,memFishnet)
        except:
            return "ERROR"       
        # define initial list of searchFields
        searchFields = ["UBID","ADMINAREAKMMASKED"]
        updateFields = ["UBID","AREAKMMASKED"]
        # create list of variables
        variables = arcpy.ListFields(estimatesFile,"*DSM")
        for variable in variables:
            name = variable.name
            newField =  name.replace("DSM","CNTM")
            # add the field
            arcpy.AddField_management(memFishnet,newField,"DOUBLE")
            # append the newField to updateFields, and the variable.name to searchFields
            updateFields.append(newField)
            searchFields.append(name)
        # create dictionary to hold source density values
        densities = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(estimatesFile,searchFields) as rows:
                for row in rows:
                    # store with UBID as key and a tuple of estimates as value
                    ubid = row[0]
                    value = row
                    densities[ubid] = value
        except:
            return "ERROR"
        # write the density estimates to estimatesFile
        try:
            # read the values
            with arcpy.da.UpdateCursor(memFishnet,updateFields) as rows:
                for row in rows:                    
                    # grab the ubid
                    ubid = row[0]
                    # grab the area
                    area = row[1]
                    # set the fields
                    i = 0
                    for field in updateFields:                        
                        if i < 2:
                            i = i + 1                            
                            pass
                        else:
                            # calculate the counts
                            row[i]= float(densities[ubid][i]) * float(area)                            
                            i = i + 1
                    
                    # update the row
                    rows.updateRow(row)
                    
        except:
            return "ERROR"
        # finally write the intersect table
        intersectTable = intersectedFishnet + "_table"
        try:
            arcpy.CopyRows_management(memFishnet,intersectTable)
        except:
            return "ERROR"
        
        # success
        return "SUCCESS for " + rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return "ERROR"

def calculateGridCounts(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-4]
    try:
        arcpy.env.workspace = gdb
        # grab intersectTable
        intersectTable = arcpy.ListTables("*_table")[0]
        fishnet = arcpy.ListFeatureClasses("*_fishnet")[0]
        # create list of fields to generate statistics for
        statsFields = [["ADMINAREAKMMASKED","MEAN"],["WATERAREAKM","SUM"],["AREAKMMASKED","SUM"]]
        # list CNTM fields in order to be flexible to whatever variables
        # are present in the country
        cntFields = arcpy.ListFields(intersectTable,"*CNTM")
        [statsFields.append([field.name,"SUM"]) for field in cntFields]
        # create a summary table in memory
        memSumTbl = 'in_memory' + os.sep + os.path.basename(intersectTable) + "_summary"
        try:
            arcpy.Statistics_analysis(intersectTable,memSumTbl,statsFields,"PIXELID")
        except:
            return "Error in " + rootName + " : making table views"
        # read the fishnet into memory
        memFishnet = 'in_memory' + os.sep + os.path.basename(fishnet) + "_view"
        try:
            arcpy.CopyFeatures_management(fishnet,memFishnet)
        except:
            return "Error in " + rootName + " : making fishnet in memory"
        # define initial list of searchFields
        searchFields = ["PIXELID"]
        updateFields = ["PIXELID"]
        # create list of variables
        variables = arcpy.ListFields(memSumTbl,"*")
        for variable in variables:
            name = variable.name
            if name == "OBJECTID":
                continue
            elif name == "PIXELID":
                continue
            elif name == "FREQUENCY":
                newField = "NUMINPUTS"
            elif name == "MEAN_ADMINAREAKMMASKED":
                newField = name
            else:
                newField =  name.replace("SUM_","")
            # add the field
            arcpy.AddField_management(memFishnet,newField,"DOUBLE")
            # append the newField to updateFields, and the variable.name to searchFields
            updateFields.append(newField)
            searchFields.append(name)
        # create dictionary to hold source counts
        counts = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(memSumTbl,searchFields) as rows:
                for row in rows:
                    # store with PIXELID as key and a tuple of estimates as value
                    pixelid = row[0]
                    value = row
                    counts[pixelid] = value
        except:
            return "Error in " + rootName + ": Creating Counts Dictionary"
        # write the density estimates to estimatesFile
        try:
            # read the values
            with arcpy.da.UpdateCursor(memFishnet,updateFields) as rows:
                for row in rows:
                    # grab the pixelid
                    pixelid = row[0]
                    if pixelid not in counts:
                        continue
                    # set the fields
                    i = 0
                    for field in updateFields:                        
                        if i < 1:
                            i = i + 1                            
                            pass
                        else:
                            # calculate the counts
                            row[i]= counts[pixelid][i]
                            i = i + 1
                    
                    # update the row
                    rows.updateRow(row)
                    
        except:
            return "Error in " + rootName + ": Writing Updates"
        # finally write the final fishnet
        finalFishnet = fishnet + "_processed"
        try:
            arcpy.CopyFeatures_management(memFishnet,finalFishnet)
        except:
            return "Error in " + rootName + ": Writing Table to Disk"
        
        # success
        return "Calculated counts for " + rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return rootName + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'H:\gpw\pop_tables'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("*")
    workspaces.sort()
    gdb_list = []
    for workspace in workspaces:        
        # describe the workspace
        workDesc = arcpy.Describe(workspace)
        # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
        if str(workDesc.workspaceType)=="FileSystem":
            workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
        gdb_list.append(workspace) 
##    for gdb in gdb_list:
##        print gdb
##        print calculateIntersectCounts(gdb)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
    successCheck = pool.map(calculateIntersectCounts, gdb_list) 
    print successCheck
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    if "ERROR" in successCheck:
        print "Script completed step 1, need to troubleshoot errors before step 2"
        print str(datetime.datetime.now()-scriptTime)
    else:
        # set workspaces and preprocess to attach paths
        inWS = r'H:\gpw\fishnets'
        #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
        arcpy.env.workspace = inWS
        workspaces = arcpy.ListWorkspaces("*")
        workspaces.sort()
        gdb_list = []
        for workspace in workspaces:        
            # describe the workspace
            workDesc = arcpy.Describe(workspace)
            # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
            if str(workDesc.workspaceType)=="FileSystem":
                workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
            gdb_list.append(workspace) 
    ##    for gdb in gdb_list:
    ##        print gdb
    ##        calculateGridCounts(gdb)
        # multiprocess the data
        pool2 = multiprocessing.Pool(processes=5,maxtasksperchild=1)
        print pool2.map(calculateGridCounts, gdb_list) 
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool2.close()
        pool2.join()
        print "Script complete"
        print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
