# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing, socket

def calculateAdminDensities(gdb):
    startTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    try:
        iso = os.path.basename(gdb)[:-4]
        host = socket.gethostname()
##        if host == 'Devsedarc3':
##            estimatesGDB = r'F:\gpw\release_4_1\input_data\pop_tables' + os.sep + iso + '.gdb'
##        elif host == 'Devsedarc4':
##            estimatesGDB = r'D:\gpw\release_4_1\input_data\pop_tables' + os.sep + iso + '.gdb'
##        arcpy.env.workspace=estimatesGDB
        arcpy.env.workspace = gdb
        estimatesIn = os.path.join(gdb,str(arcpy.ListTables("*estimates")[0]))
        adminBoundaries = arcpy.ListFeatureClasses("*_gridding")[0]
        # define initial list of searchFields
        boundarySearchFields = ["UBID","MASKEDAREA"]
        searchFields = ["UBID","MASKEDADMINAREA"]
        updateFields = ["UBID","MASKEDADMINAREA"]
        # create in memory estimates file
        inMemEstimates = "in_memory" + os.sep + os.path.basename(estimatesIn)
        try:
            arcpy.CopyRows_management(estimatesIn,inMemEstimates)
        except:
            return "Error creating " + inMemEstimates
        
        # add ADMINAREAKMMASKED
##        arcpy.AddField_management(inMemEstimates,"MASKEDADMINAREA","DOUBLE")
        # create list of variables
        eVariables = arcpy.ListFields(inMemEstimates,"E_*")
        uneVariables = arcpy.ListFields(inMemEstimates,"UNE_*")
        variables = eVariables + uneVariables
        for variable in variables:
            newField = variable.name + "_DSM"
            # add the field
            if len(arcpy.ListFields(inMemEstimates,newField))==0:
                arcpy.AddField_management(inMemEstimates,newField,"DOUBLE")
            # append the newField to updateFields, and the variable.name to searchFields
            updateFields.append(newField)
            searchFields.append(variable.name)
        # create dictionary to hold area values
        areas = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(adminBoundaries,boundarySearchFields) as rows:
                for row in rows:
                    # store with UBID as key 
                    key = row[0]
                    # store the area estimate as value
                    value = row[1]
                    
                    areas[key] = value
        except:
            return "Error in " + iso + ": Creating Areas Dictionary"
        # create dictionary to hold source estimates values
        estimates = {}
##        return searchFields
        try:
            # read the values
            with arcpy.da.SearchCursor(inMemEstimates,searchFields) as rows:
                for row in rows:
##                    return (searchFields, row)
                    # store with UBID as key and a tuple of estimates as value
                    key = row[0]
                    value = row
                    estimates[key] = value
        except:
            return "Error in " + iso + ": Creating Estimates Dictionary"
        # write the density estimates to estimatesFile
        try:
            # read the values
            with arcpy.da.UpdateCursor(inMemEstimates,updateFields) as rows:
                for row in rows:                    
                    # grab the ubid
                    ubid = row[0]
                    if ubid in estimates:
                        # grab the area
                        if ubid in areas:
                            area = areas[ubid]
                        else:
                            area = 0
                        # set the fields
                        i = 0
                        for field in updateFields:
                            #print row
                            if i < 1:
                                i = i + 1                            
                                pass
                            elif i < 2:
                                row[i]=area
                                i = i + 1
                            else:
                                # calculate the proportions
                                try:
                                    row[i]= float(estimates[ubid][i]) / float(area)
                                except:
                                    row[i]= 0
                                i = i + 1                            
                    
                    # update the row
                    rows.updateRow(row)
                
        except:
            return "Error in " + iso + ": Writing Updates: " + str(row)
        # write table back to disk
        try:
            estimatesFile = os.path.join(gdb,os.path.basename(estimatesIn))
            arcpy.CopyRows_management(inMemEstimates,estimatesFile)
        except:
            return "Error writing " + outTable
        
        # success
        return "Calculated administrative densities for " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    host = socket.gethostname()
    if host == 'Devsedarc3':
        workspace = r'F:\gpw\release_4_1\process'
    elif host == 'Devsedarc4':
        workspace = r'D:\gpw\release_4_1\process'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    gdbs= arcpy.ListWorkspaces("grl*")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
    pool = multiprocessing.Pool(processes=18,maxtasksperchild=1)
    results = pool.map(calculateAdminDensities, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
