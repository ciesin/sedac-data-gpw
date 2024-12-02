# this script applies the proportions of a demographic to
# ATOTPOPBT to produce demographic estimates in year 2010

import arcpy, os, datetime, multiprocessing

def applyProportions(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:6]
    arcpy.env.workspace = gdb
    try:
        proportions = arcpy.ListTables("*usgrids_pop_proportions")[0]
        estimatesFile = arcpy.ListTables("*estimates")[0]
        # need to also add and calculate AGEID, and APOPYEAR and APOPLEVEL
##        arcpy.AddField_management(estimatesFile,"AGEID","TEXT","","",200)
##        arcpy.AddField_management(estimatesFile,"APOPYEAR","SHORT")
##        arcpy.AddField_management(estimatesFile,"APOPLEVEL","SHORT")
        # define initial list of searchFields
        searchFields = ["UBID"]
        updateFields = ["E_ATOTPOPBT_2010","UBID"]
        # create list of variables
        variables = ["WOMCHILD"]
##                     ["WHITE","BLACK","AMIND","ASIAN","HAWPI",
##                     "HISP","NHISP","NHWHITE","NHBLACK","OTHER",
##                     "TWOMORE","PUND25","P25","AUND1","A1TO4",
##                     "A5TO17","A18TO24","A25TO64","A65TO79","AOV80"]
        for variable in variables:
            newField = 'E_' + variable + '_2010'
            # add the field
            if len(arcpy.ListFields(estimatesFile,newField))==0:
                arcpy.AddField_management(estimatesFile,newField,"DOUBLE")
            else:
                return gdb + " was already processed"
            updateFields.append(newField)
            propField = variable +"_PROP"
            searchFields.append(propField)       

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
                    # grab the total pop estimate
                    totpop = row[0]                    
                    # grab the ubid
                    ubid = row[1]                    
                    # set the fields
                    i = 0
                    for field in updateFields:                        
                        if i < 2:
                            i = i + 1                            
                            pass                       
                        else:
                            # calculate the proportions
                            row[i]= float(values[ubid][i-1]) * float(totpop)                            
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
        print applyProportions(gdb)
    # multiprocess the data
##    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
##    print pool.map(applyProportions, gdb_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
