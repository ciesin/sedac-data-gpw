# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing, socket

def calculateIntersectCounts(gdb):
    arcpy.env.overwriteOutput = True
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-4]
    try:
        arcpy.env.workspace = gdb
        # grab estimatesFile
        estimatesFile = arcpy.ListTables("*estimates")[0]
        # there may be more than one intersectedFishnet if the data has a boundary context
        intersectedFishnets = arcpy.ListFeatureClasses("*_intersect")
        waterFeatures = arcpy.ListFeatureClasses("*water*intersect*")
        waterDict = {}
        if len(waterFeatures)==1:
            waterFeature = waterFeatures[0]
            try:
                # read the values
                with arcpy.da.SearchCursor(waterFeature,["UBID","WATERAREAKM"]) as rows:
                    for row in rows:
                        # store with UBID as key and a tuple of estimates as value
                        ubid = row[0]
                        value = row[1]
                        waterDict[ubid] = value
            except:
                return "Error in " + rootName + ": Creating Water Dictionary"
        intersectTable = gdb + os.sep + rootName + "_intersect_estimates_table"
##        if not arcpy.Exists(intersectTable):
        # read the files into memory
        memFishnet = 'in_memory' + os.sep + rootName + "_view"
        # if there is only 1 intersected fishnet we will copy it into memory
        # if there is more than 1 we will copy 1 and append the other
        if len(intersectedFishnets)==1:
            try:
                intersectedFishnet = intersectedFishnets[0]
                arcpy.CopyRows_management(intersectedFishnet,memFishnet)
            except:
                return "Error in " + rootName + " : making table views"
        elif len(intersectedFishnets)>1:
            try:
                intersectedFishnet = intersectedFishnets[0]
                arcpy.CopyRows_management(intersectedFishnet,memFishnet)
                tmp = 'in_memory' + os.sep + rootName + "_temp"
                arcpy.CopyRows_management(intersectedFishnets[1],tmp)
                arcpy.Append_management(tmp,memFishnet,"NO_TEST")
            except:
                return "Error in " + rootName + " : making table views and appending " + str(arcpy.GetMessages())
        else:
            return "Error in " + rootName + " missing intersect tables"
        # define initial list of searchFields
        searchFields = ["UBID","MASKEDADMINAREA"]
        updateFields = ["UBID","BOUNDARY_CONTEXT","AREAKM","WATERAREAKM","AREAKMMASKED"]
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
                    bc = row[1]
                    # grab the area
                    areakm = row[2]
                    waterareakm = row[3]
                    areakmmasked = row[4]
                    if areakmmasked == None:
                        if ubid in waterDict:
                            row[3]=waterDict[ubid]
                            waterareakm = row[3]
                        else:
                            row[3]=0
                            waterareakm = row[3]
                        maskCalc = float(areakm)-waterareakm
                        if maskCalc<0:
                            maskCalc=0
                        row[4]=maskCalc
                    # set the fields
                    area = row[4]
                    i = 0
                    j = -3
                    for field in updateFields:                        
                        if i < 5:
                            i = i + 1
                            j = j + 1
                            pass
                        else:
                            if not ubid in densities:
                                row[i]= 0
                            else:
                                # calculate the counts
                                row[i]= float(densities[ubid][j]) * float(area)
                            i = i + 1
                            j = j + 1
                    # update the row
                    rows.updateRow(row)
        except:
            return "Error in " + rootName + ": Writing Updates: " + str(row)
        # finally write the intersect table
        try:
            arcpy.CopyRows_management(memFishnet,intersectTable)
        except:
            return "Error in " + rootName + ": Writing Table to Disk"
##        else:
##            return "Already processed " + rootName
        
        # success
        return "Calculated intersected counts for " + rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return rootName + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    host = socket.gethostname()
    if host == 'Devsedarc3':
        inWS = r'F:\gpw\release_4_1\process'
    elif host == 'Devsedarc4':
        inWS = r'D:\gpw\release_4_1\process'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = [os.path.join(inWS,workspace) for workspace in arcpy.ListWorkspaces("grl*")]
    workspaces.sort()
    print workspaces
    # multiprocess the data
    pool = multiprocessing.Pool(processes=18,maxtasksperchild=1)
    results = pool.map(calculateIntersectCounts, workspaces)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
