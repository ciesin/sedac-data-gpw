# this script applies the proportions of a demographic to
# ATOTPOPBT to produce demographic estimates in year 2010

import arcpy, os, datetime, multiprocessing

def applyProportions(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    arcpy.env.workspace = gdb
    try:
        urProportions = arcpy.ListTables("*_ur_proportions")[0]
        estimatesFile = arcpy.ListTables("*estimates")[0]
        # need to also add and calculate AGEID, and APOPYEAR and APOPLEVEL
        arcpy.AddField_management(estimatesFile,"URID","TEXT","","",200)
        arcpy.AddField_management(estimatesFile,"URPOPYEAR","SHORT")
        arcpy.AddField_management(estimatesFile,"URPOPLEVEL","SHORT")
        # define initial list of searchFields
        uridSearchFields = ["URID_SOURCE"]
        searchFields = ["URID","URPOPYEAR","URPOPLEVEL"]
        updateFields = ["E_ATOTPOPBT_2010","URID","URPOPYEAR","URPOPLEVEL"]
        # create list of variables
        variables = ["ATOTPOPBU","ATOTPOPBR","ATOTPOPFU","ATOTPOPFR","ATOTPOPMU","ATOTPOPMR"]
        for variable in variables:
            newField = 'E_' + variable + '_2010'
            # add the field
            arcpy.AddField_management(estimatesFile,newField,"DOUBLE")
            updateFields.append(newField)
            propField = variable +"_PROP"
            searchFields.append(propField)
        # parse URID_SOURCE
        if iso =="usa":
            # check for URID_SOURCE
            if len(arcpy.ListFields(urProportions,"URID_SOURCE"))==0:
                arcpy.AddField_management(urProportions,"URID","TEXT")
                arcpy.AddField_management(urProportions,"URID_SOURCE","TEXT")
                arcpy.AddField_management(urProportions,"URPOPLEVEL","SHORT")
                arcpy.AddField_management(urProportions,"URPOPYEAR","SHORT")
                arcpy.CalculateField_management(urProportions,"URID_SOURCE",
                                                '"' + "UCADMIN0_UCADMIN1_UCADMIN2_UCADMIN3_UCADMIN4_UCADMIN5" + '"',
                                                "PYTHON")
                arcpy.CalculateField_management(urProportions,"URID",
                                                """!UCADMIN0! + '_' + !UCADMIN1! + '_' + !UCADMIN2! + '_' + !UCADMIN3! + '_' + !UCADMIN4! + '_' + !UCADMIN5! """,
                                                "PYTHON")
                arcpy.CalculateField_management(urProportions,"URPOPLEVEL",5,"PYTHON")
                arcpy.CalculateField_management(urProportions,"URPOPYEAR",2010,"PYTHON")
        
        # search fields to calculate URID
        with arcpy.da.SearchCursor(urProportions,uridSearchFields) as rows:
            for row in rows:
                # grab values
                URIDSOURCE = str(row[0])
                break     
        for urItem in URIDSOURCE.split("_"):
            if urItem == URIDSOURCE.split("_")[0]:
                expression = "!" + urItem + "!"
            else:
                expression = expression + '+"_"+' + "!" + urItem + "!"
        arcpy.CalculateField_management(estimatesFile,"URID",expression,"PYTHON")

        # create dictionary to hold values
        values = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(urProportions,searchFields) as rows:
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
                    urid = row[1]                    
                    # set the fields
                    i = 0
                    for field in updateFields:                        
                        if i < 2:
                            i = i + 1                            
                            pass
                        elif i < 4:
                            row[i]=values[urid][i-1]
                            i = i + 1
                        else:
                            # calculate the proportions
                            row[i]= float(values[urid][i-1]) * float(totpop)                            
                            i = i + 1
                    
                    # update the row
                    rows.updateRow(row)
                    
        except:
            return "Error in " + iso + ": Writing Value Dictionary"
        
        # success
        return "Applied UR Proportions for " + iso + ": " + str(datetime.datetime.now()-startTime)
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
    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
    print pool.map(applyProportions, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
