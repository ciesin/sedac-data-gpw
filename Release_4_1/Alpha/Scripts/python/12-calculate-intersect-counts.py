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
        # check if fishGDB exists, if not create a list of gdbs to process
        if arcpy.Exists(fishGDB):
            fishList = [fishGDB]
        else:
            # create list of workspaces
            arcpy.env.workspace = os.path.dirname(os.path.dirname(gdb)).replace("pop_tables","fishnets")
            workspaces = arcpy.ListWorkspaces(rootName + "*")
            fishList = []
            for ws in workspaces:
                fishList.append(ws)
        for fishGDB in fishList:   
            arcpy.env.workspace = fishGDB
            intersectedFishnet = arcpy.ListFeatureClasses("*_intersect")[0]
            intersectTable = intersectedFishnet + "_table"
            if not arcpy.Exists(intersectTable):
                # read the files into memory
                memFishnet = 'in_memory' + os.sep + os.path.basename(intersectedFishnet) + "_view"
                try:
                    arcpy.CopyRows_management(intersectedFishnet,memFishnet)
                except:
                    return "Error in " + rootName + " : making table views"       
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
                    return "Error in " + rootName + ": Creating Densities Dictionary"
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
                                    if not ubid in densities:
                                        row[i]= 0
                                    else:
                                        # calculate the counts
                                        row[i]= float(densities[ubid][i]) * float(area)
                                    i = i + 1
                            
                            # update the row
                            rows.updateRow(row)
                except:
                    return "Error in " + rootName + ": Writing Updates: " + str(row)
                # finally write the intersect table
                try:
                    arcpy.CopyRows_management(memFishnet,intersectTable)
                except:
                    return "Error in " + rootName + ": Writing Table to Disk"
            else:
                return "Already processed " + rootName
            
        # success
        return "Calculated intesected counts for " + rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return rootName + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\stage\pop_tables'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("*","FILEGDB")
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
    pool = multiprocessing.Pool(processes=22,maxtasksperchild=1)
    print pool.map(calculateIntersectCounts, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
