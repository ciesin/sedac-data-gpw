# this script applies the proportions of a demographic to
# ATOTPOPBT to produce demographic estimates in year 2010

import arcpy, os, datetime, multiprocessing

def applyProportions(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    arcpy.env.workspace = gdb
##    if os.path.basename(gdb)=="vcs.gdb":
##        return iso + " does not have sex data"
    try:
        ageProportions = arcpy.ListTables("*age_5_year_proportions")[0]
        estimatesFile = arcpy.ListTables("*estimates")[0]
        # need to also add and calculate AGEID, and APOPYEAR and APOPLEVEL
        arcpy.AddField_management(estimatesFile,"AGEID","TEXT","","",200)
        arcpy.AddField_management(estimatesFile,"APOPYEAR","SHORT")
        arcpy.AddField_management(estimatesFile,"APOPLEVEL","SHORT")
        # define initial list of searchFields
        ageidSearchFields = ["AGEID_SOURCE"]
        searchFields = ["AGEID","APOPYEAR","APOPLEVEL"]
        updateFields = ["E_ATOTPOPBT_2010","AGEID","APOPYEAR","APOPLEVEL"]
        # define age fields
        ageFields = ['A000_004BT','A005_009BT','A010_014BT','A015_019BT','A020_024BT','A025_029BT',
                    'A030_034BT','A035_039BT','A040_044BT','A045_049BT','A050_054BT','A055_059BT',
                    'A060_064BT','A065_069BT','A070_074BT','A075_079BT','A080_084BT','A085plusBT']
        for ageField in ageFields:
            newField = 'E_' + ageField + '_2010'
            # add the field
            arcpy.AddField_management(estimatesFile,newField,"DOUBLE")
            updateFields.append(newField)
            propField = ageField +"PROP"
            searchFields.append(propField)
        # parse AGEID_SOURCE
        if iso =="usa":
            # check for AGEID_SOURCE
            if len(arcpy.ListFields(ageProportions,"AGEID_SOURCE"))==0:
                arcpy.AddField_management(ageProportions,"AGEID","TEXT")
                arcpy.AddField_management(ageProportions,"AGEID_SOURCE","TEXT")
                arcpy.AddField_management(ageProportions,"APOPLEVEL","SHORT")
                arcpy.AddField_management(ageProportions,"APOPYEAR","SHORT")
                arcpy.CalculateField_management(ageProportions,"AGEID_SOURCE",
                                                '"' + "UCADMIN0_UCADMIN1_UCADMIN2_UCADMIN3_UCADMIN4_UCADMIN5" + '"',
                                                "PYTHON")
                arcpy.CalculateField_management(ageProportions,"AGEID",
                                                """!UCADMIN0! + '_' + !UCADMIN1! + '_' + !UCADMIN2! + '_' + !UCADMIN3! + '_' + !UCADMIN4! + '_' + !UCADMIN5! """,
                                                "PYTHON")
                arcpy.CalculateField_management(ageProportions,"APOPLEVEL",5,"PYTHON")
                arcpy.CalculateField_management(ageProportions,"APOPYEAR",2010,"PYTHON")
        
        # search fields to calculate AGEID
        with arcpy.da.SearchCursor(ageProportions,ageidSearchFields) as rows:
            for row in rows:
                # grab values
                AGEIDSOURCE = str(row[0])
                break     
        for ageItem in AGEIDSOURCE.split("_"):
            if ageItem == AGEIDSOURCE.split("_")[0]:
                expression = "!" + ageItem + "!"
            else:
                expression = expression + '+"_"+' + "!" + ageItem + "!"
        arcpy.CalculateField_management(estimatesFile,"AGEID",expression,"PYTHON")
        # create dictionary to hold values
        values = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(ageProportions,searchFields) as rows:
                for row in rows:
                    # store with AGEID as key and a tuple of numbers as value
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
                    # grab the ageid
                    ageid = row[1]
                    # set the fields
                    i = 0
                    for field in updateFields:
                        if i < 2:
                            i = i + 1
                            pass
                        elif i < 4:
                            row[i]=values[ageid][i-1]
                            i = i + 1
                        else:
                            # calculate the proportions
                            row[i]= float(values[ageid][i-1]) * float(totpop)
                            i = i + 1
                    # update the row
                    rows.updateRow(row)
                    
        except:
            return "Error in " + iso + ": Writing Value Dictionary"
        
        # success
        return "Applied Age Proportions for " + iso + ": " + str(datetime.datetime.now()-startTime)
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
##        print unAdjust(workspace)
##        for gdb in gdb_list:
##            applyProportions(gdb)
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
