# this script applies the proportions of a demographic to
# ATOTPOPBT to produce demographic estimates in year 2010

##PLEASE NOTE I WAS LAZY AND DID NOT RENAME VARIABLES EVEN THOUGH THIS
##SCRIPT JUST JOINS AND DOES NOT APPLY PROPORTIONS>>>SORRY!!!  KYTT

import arcpy, os, datetime, multiprocessing

def applyProportions(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:6]
    arcpy.env.workspace = gdb
    try:
        proportions = arcpy.ListTables("*usgrids_hh_proportions")[0]
        estimatesFile = arcpy.ListTables("*estimates")[0]
        # define initial list of searchFields
        searchFields = ["UBID"]
        updateFields = ["UBID"]
        # create list of variables
        variables = ["HH","FEM","HU","OCC","OWN","SEA","HU1P"]
        for variable in variables:
            newField = 'E_' + variable + '_2010'
            # add the field
            arcpy.AddField_management(estimatesFile,newField,"DOUBLE")
            updateFields.append(newField)
            searchFields.append(variable)       

        # create dictionary to hold values
        values = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(proportions,searchFields) as rows:
                for row in rows:
                    # store with UBID as key and a tuple of numbers as value
                    key = row[0]
                    value = row
                    values[key] = value
        except:
            return "Error in " + iso + ": Creating Value Dictionary"
        try:
            # read the values
            with arcpy.da.UpdateCursor(estimatesFile,updateFields) as rows:
                for row in rows:                 
                    # grab the ubid
                    ubid = row[0]                    
                    # set the fields
                    i = 0
                    for field in updateFields:                        
                        if i < 1:
                            i = i + 1                            
                            pass                       
                        else:
                            # ADD THE DATA  
                            row[i]= values[ubid][i]                           
                            i = i + 1
                    
                    # update the row
                    rows.updateRow(row)
                    
        except:
            return "Error in " + iso + ": Writing Value Dictionary"
        
        # success
        return "Applied USGRID Proportions for " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

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
##        print applyProportions(gdb)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=6,maxtasksperchild=1)
    print pool.map(applyProportions, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
