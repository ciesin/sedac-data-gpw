# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing

def calculateGridCounts(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-4]
    try:
        arcpy.env.workspace = gdb
        arcpy.env.overwriteOutput = True
        # grab intersectTable
        intersectTable = arcpy.ListTables("*_table")[0]
        fishnet = arcpy.ListFeatureClasses("*_fishnet")[0]
        finalFishnet = fishnet + "_processed"
##        if arcpy.Exists(finalFishnet):
##            return rootName + " : already processed"
        # create list of fields to generate statistics for
        statsFields = []
        # list CNTM fields in order to be flexible to whatever variables
        # are present in the country
        cntFields = arcpy.ListFields(intersectTable,"*WOMCHILD*CNTM")
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
            arcpy.CopyFeatures_management(finalFishnet,memFishnet)
        except:
            return "Error in " + rootName + " : making fishnet in memory"
        # define initial list of searchFields
        searchFields = ["PIXELID"]
        updateFields = ["PIXELID"]
        # create list of variables
        variables = arcpy.ListFields(memSumTbl,"*WOMCHILD*")
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
    inWS = r'H:\gpw\stage\fishnets'
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
            workspace = workspace + os.sep + 'tiles'
            arcpy.env.workspace = workspace
            gdbs = arcpy.ListWorkspaces("*")
            for gdb in gdbs:
                gdb_list.append(gdb)
        else:
            gdb_list.append(workspace) 
    for gdb in gdb_list:
        print gdb
        print calculateGridCounts(gdb)
    # multiprocess the data
##    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
##    print pool.map(calculateGridCounts, gdb_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
