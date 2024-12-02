# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing

def calculateAdminDensities(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    arcpy.env.workspace = gdb
    arcpy.env.overwriteOutput = True
    try:
        adminBoundaries = arcpy.ListFeatureClasses("*_gridding")[0]
        estimatesFile = arcpy.ListTables("*estimates")[0]
        delFields = arcpy.ListFields(estimatesFile,"*DSM")
        if len(delFields)>0:
            delNames = []
            for fld in delFields:
                delNames.append(fld.name)
            print delNames
            arcpy.DeleteField_management(estimatesFile,delNames)
        # define initial list of searchFields
        boundarySearchFields = ["UBID","ADMINAREAKMMASKED"]
        searchFields = ["UBID","ADMINAREAKMMASKED"]
        updateFields = ["UBID","ADMINAREAKMMASKED"]
        # add ADMINAREAKMMASKED
        arcpy.AddField_management(estimatesFile,"ADMINAREAKMMASKED","DOUBLE")
        # create list of variables
        eVariables = arcpy.ListFields(estimatesFile,"E_*")
        uneVariables = arcpy.ListFields(estimatesFile,"UNE_*")
        variables = eVariables + uneVariables
        for variable in variables:
            newField = variable.name + "_DSM"
            # add the field
            if len(arcpy.ListFields(estimatesFile,newField))==0:
                arcpy.AddField_management(estimatesFile,newField,"DOUBLE")
            # append the newField to updateFields, and the variable.name to searchFields
            updateFields.append(newField)
            searchFields.append(variable.name)
        # create in memory estimates file
        inMemEstimates = "in_memory" + os.sep + os.path.basename(estimatesFile)
        try:
            arcpy.CopyRows_management(estimatesFile,inMemEstimates)
        except:
            return "Error creating " + inMemEstimates
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
        try:
            # read the values
            with arcpy.da.SearchCursor(estimatesFile,searchFields) as rows:
                for row in rows:
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
        outTable = gdb + os.sep + os.path.basename(estimatesFile)
        try:
            arcpy.CopyRows_management(inMemEstimates,estimatesFile)
        except:
            return "Error writing " + outTable
        
        # success
        return "Calculated administrative densities for " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'H:\gpw\stage\pop_tables'
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
    for gdb in gdb_list:
        print gdb
        print calculateAdminDensities(gdb)
    # multiprocess the data
##    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
##    print pool.map(calculateAdminDensities, gdb_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
