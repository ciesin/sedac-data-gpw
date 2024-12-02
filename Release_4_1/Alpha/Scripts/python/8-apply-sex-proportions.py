# this script applies the proportions of a demographic to
# ATOTPOPBT to produce demographic estimates in year 2010

import arcpy, os, datetime, multiprocessing

def applyProportions(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        return iso + " does not have sex data"
    try:
        sexProportions = arcpy.ListTables("*sex_variables_proportions")[0]
        estimatesFile = arcpy.ListTables("*estimates")[0]
        # first preprocess the sexFile
        # try to add ATOTPOPMT and ATOTPOPFT
        arcpy.AddField_management(estimatesFile,"E_ATOTPOPMT_2010","DOUBLE")
        arcpy.AddField_management(estimatesFile,"E_ATOTPOPFT_2010","DOUBLE")
        # need to also add and calculate VARID, and SPOPYEAR and SPOPLEVEL
        arcpy.AddField_management(estimatesFile,"VARID","TEXT","","",200)
        arcpy.AddField_management(estimatesFile,"SPOPYEAR","SHORT")
        arcpy.AddField_management(estimatesFile,"SPOPLEVEL","SHORT")
        # parse VARID_SOURCE to create expression and grab year
        if iso =="usa":
            # check for VARID_SOURCE
            if len(arcpy.ListFields(sexProportions,"VARID_SOURCE"))==0:
                arcpy.AddField_management(sexProportions,"VARID","TEXT")
                arcpy.AddField_management(sexProportions,"VARID_SOURCE","TEXT")
                arcpy.CalculateField_management(sexProportions,"VARID_SOURCE",
                                                '"' + "UCADMIN0_UCADMIN1_UCADMIN2_UCADMIN3_UCADMIN4_UCADMIN5" + '"',
                                                "PYTHON")
                arcpy.CalculateField_management(sexProportions,"VARID",
                                                """!UCADMIN0! + '_' + !UCADMIN1! + '_' + !UCADMIN2! + '_' + !UCADMIN3! + '_' + !UCADMIN4! + '_' + !UCADMIN5! """,
                                                "PYTHON")
        
        with arcpy.da.SearchCursor(sexProportions,["VARID_SOURCE","RPOPYEAR"]) as rows:
            for row in rows:
                VARIDSOURCE = str(row[0])
                SPOPYEAR = int(row[1])
                break
        # calculate level and year
        arcpy.CalculateField_management(estimatesFile,"SPOPYEAR",SPOPYEAR,"PYTHON")
        SPOPLEVEL = len(VARIDSOURCE.split("_"))-1
        arcpy.CalculateField_management(estimatesFile,"SPOPLEVEL",SPOPLEVEL,"PYTHON")
        
            
        for varItem in VARIDSOURCE.split("_"):
            if varItem == VARIDSOURCE.split("_")[0]:
                expression = "!" + varItem + "!"
            else:
                expression = expression + '+"_"+' + "!" + varItem + "!"
        arcpy.CalculateField_management(estimatesFile,"VARID",expression,"PYTHON")
        # Make Feature Layers
        layer1 = os.path.basename(estimatesFile) + "_lyr"
        layer2 = os.path.basename(sexProportions) + "_lyr"
        joinFeature = sexProportions
        if not arcpy.Exists(layer1):
            try:
                arcpy.MakeFeatureLayer_management(estimatesFile,layer1)
            except:
                arcpy.MakeTableView_management(estimatesFile,layer1)
        if not arcpy.Exists(layer2):
            try:
                arcpy.MakeFeatureLayer_management(joinFeature,layer2)
            except:
                arcpy.MakeTableView_management(joinFeature,layer2)
        # Add Join
        joinField = "VARID"
        arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_COMMON")
        # define fields to join
        mProp = "ATOTPOPMTPROP"
        fProp = "ATOTPOPFTPROP"
        joinVariables = [mProp,fProp]
        for joinVariable in joinVariables:
            if joinVariable == mProp:
                sField = os.path.basename(estimatesFile) + ".E_ATOTPOPMT_2010"
            elif joinVariable == fProp:
                sField = os.path.basename(estimatesFile) + ".E_ATOTPOPFT_2010"
            expression = '!' + os.path.basename(joinFeature) + "." + joinVariable + '!*!' + os.path.basename(estimatesFile) + ".E_ATOTPOPBT_2010!"
            arcpy.CalculateField_management(layer1,sField,expression,'PYTHON')
        # success
        return "Applied Sex Proportions for " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\stage\new_inputs\pop_tables'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("pol*")
    workspaces.sort()
    gdb_list = []
    for workspace in workspaces:
        # describe the workspace
        workDesc = arcpy.Describe(workspace)
        # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
        if str(workDesc.workspaceType)=="FileSystem":
            workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
        gdb_list.append(workspace) 
        print applyProportions(workspace)
    # multiprocess the data
##    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
##    print pool.map(applyProportions, gdb_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
