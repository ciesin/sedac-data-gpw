## the pop_tables directory contains all of the input population tables.
## they were preprocessed in this directory
## the country_boundaries_hi_res.gdb contains the input geographic boundaries
## they were exported from ArcSDE and post-processed to remove any features
## that were waterbodies in order to treat water instead with the application
## of a water mask.

# this script will validate the population tables by summing them nationally
# and comparing them to the total population in 2010. E_ATOTPOPBT_2010

# this script will also validate the joining of the estimates table to the
# boundaries

# import libraries
import arcpy, csv, os, datetime, multiprocessing

def summarizeEstimates(gdb):
    '''A Function to summarize the estimates tables for variables'''
    arcpy.env.overwriteOutput = True
    # first grab the estimates table
    arcpy.env.workspace = gdb
    estimatesFile = arcpy.ListTables("*estimates")[0]
    # generate a list of fields to summarize
    estimateFields = arcpy.ListFields(estimatesFile,"E*")
    # create a summary list
    summaryFields = [[str(estimateField.name),"SUM"] for estimateField in estimateFields]
    # summarize the results 
    summaryTable = gdb + os.sep + os.path.basename(estimatesFile)+ "_variables_summary"
    arcpy.Statistics_analysis(estimatesFile,summaryTable,summaryFields,"ISO")
    return summaryTable

def validateJoin(gdb):
    '''A Function to validate the estimates to boundaries join'''
    arcpy.env.overwriteOutput = True
    # first grab the estimates table
    arcpy.env.workspace = gdb
    estimatesFile = gdb + os.sep + arcpy.ListTables("*estimates")[0]
    # count the rows
    estimatesCount = arcpy.GetCount_management(estimatesFile)[0]
    # next get the boundary file
    countryISO = os.path.basename(gdb)[:3]
    if countryISO == "usa":
        boundaryGDB = r"D:\gpw\us_boundaries_hi_res.gdb"
        iso = os.path.basename(gdb)[:6]
    else:
        boundaryGDB = r"D:\gpw\country_boundaries_hi_res.gdb"
        iso = countryISO
    arcpy.env.workspace = boundaryGDB
    boundaryFile = arcpy.ListFeatureClasses("*"+iso+"*")[0]
    # count the rows
    boundaryCount = arcpy.GetCount_management(boundaryFile)[0]
    # create in memory representation and test the join
    layer1 = os.path.basename(boundaryFile) + "_lyr"
    arcpy.MakeFeatureLayer_management(boundaryFile,layer1)
    layer2 = os.path.basename(estimatesFile) + "_lyr"
    arcpy.MakeTableView_management(estimatesFile,layer2)
    joinField = "UBID"
    # count the rows
    joinCount = arcpy.GetCount_management(
        arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_COMMON"))[0]
    return [iso,estimatesCount,boundaryCount,joinCount]
    
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
##    for gdb in gdb_list:
##        print gdb
##        print summarizeEstimates(gdb)
    # multiprocess the summaries
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    summaryTables = pool.map(summarizeEstimates, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    # iterate the summaryTables and examine the results
    # write them to a csv
    outFile = inWS + os.sep + 'input_validation_results.csv'
    csvFile = csv.writer(open(outFile,'wb'))
    summaryTemplate = summaryTables[0]
    templateFields = arcpy.ListFields(summaryTemplate,"*")
    header = tuple([templateField.name if templateField.name[:3]<>"SUM" else templateField.name[4:] for templateField in templateFields])
    csvFile.writerow(header)
    for summaryTable in summaryTables:
        with arcpy.da.SearchCursor(summaryTable,"*") as cursor:
            for row in cursor:
                csvFile.writerow(row)
    del csvFile
##    for gdb in gdb_list:
##        print gdb
##        print validateJoin(gdb)
    # now multiprocess the join validation
    pool2 = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    countTuples = pool2.map(validateJoin, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool2.close()
    pool2.join()
    # iterate the countTuples and examine the results
    # write them to a csv
    outFile2 = inWS + os.sep + 'join_validation_results.csv'
    csvFile2 = csv.writer(open(outFile2,'wb'))
    header =("ISO","ESTIMATESROWS","BOUNDARYROWS","JOINROWS","UNJOINED")
    csvFile2.writerow(header)
    for countTuple in countTuples:
        countTuple.append(int(countTuple[2])-int(countTuple[3]))
        csvFile2.writerow(tuple(countTuple))
    del csvFile2
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
