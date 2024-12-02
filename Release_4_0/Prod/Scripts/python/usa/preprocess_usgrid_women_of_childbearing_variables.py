# create input usgrids tables
# this script has custom considerations that may make it difficult to reuse in its entirety
# however there may be useful snippets for reuse
# Kytt MacManus

import arcpy, os, sys, datetime, multiprocessing

def copyTables(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:-4]
    if iso == 'pri':
        # sf1tables
        inputTable = r'H:\gpw\sf1_women_childbearing.gdb' + os.sep + iso       
    else:
        inputTable = r'H:\gpw\sf1_women_childbearing.gdb'+ os.sep + iso.split("_")[1]
    # first deal with the pop data
    if iso.split("_")[1][:2]=="ak":
        popTable = gdb + os.sep +  'usa_ak_admin5_2010_usgrids_pop_input'
    else:
        popTable = gdb + os.sep +  iso + '_admin5_2010_usgrids_pop_input'
    # read into memory
    memTbl = 'in_memory' + os.sep + iso + "_view"
    print inputTable
    print popTable
    print memTbl
    try:
        arcpy.CopyRows_management(popTable,memTbl)
    except:
        return "Error in " + iso + " : making fishnet in memory: " + str(arcpy.GetMessages())

     # define initial list of searchFields
    searchFields = ["UBID","WOMCHILD"]
    updateFields = ["UBID","WOMCHILD"]
    arcpy.AddField_management(memTbl,"WOMCHILD","DOUBLE")
    # create dictionary to hold source counts
    counts = {}
    try:
        # read the values
        with arcpy.da.SearchCursor(inputTable,searchFields) as rows:
            for row in rows:
                # store with PIXELID as key and a tuple of estimates as value
                pixelid = row[0]
                value = row[1]
                counts[pixelid] = value
    except:
        return "Error in " + iso + ": Creating Counts Dictionary"
    # write the density estimates to estimatesFile
    try:
        # read the values
        with arcpy.da.UpdateCursor(memTbl,updateFields) as rows:
            for row in rows:
                # grab the pixelid
                pixelid = row[0]
                
                # set the fields
                i = 0
                for field in updateFields:
                    if i < 1:
                        i = i + 1                            
                        pass
                    elif pixelid not in counts:
                        row[1]= 0                       
                        i = i + 1
                    else:
                        # calculate the counts
                        row[1]= counts[pixelid]                        
                        i = i + 1
                
                # update the row
                rows.updateRow(row)
                
    except:
        return "Error in " + iso + ": Writing Updates"
    # finally write the final fishnet
    try:
        arcpy.Rename_management(popTable,popTable+"_beta")
        arcpy.CopyRows_management(memTbl,popTable)
        arcpy.Delete_management(popTable+"_beta")
    except:
        return "Error in " + iso + ": Writing Table to Disk : " + str(arcpy.GetMessages())
    
    
    # print total time to run
    return iso + ": " + str(datetime.datetime.now()-startTime)
    


def main():
    startTime = datetime.datetime.now()
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'H:\gpw\stage\pop_tables' # on machine devsedarc2
    arcpy.env.workspace = workspace
    gdbs = arcpy.ListWorkspaces('**',"FILEGDB")
    gdbs.sort()
    gdb_list = [os.path.join(workspace, gdb) for gdb in gdbs]
    print len(gdb_list)
    for gdb in gdb_list:
        print gdb
        print copyTables(gdb)
        
##    pool = multiprocessing.Pool(processes=28,maxtasksperchild=1)
##    try:
##        print pool.map(copyTables, gdb_list)
##        # Synchronize the main process with the job processes to
##        # ensure proper cleanup.
##        pool.close()
##        pool.join()
##    except:
##        print sys.stdout
##        pool.close()
##        pool.join()
    # End main
    print "Script Complete: " + str(datetime.datetime.now()-startTime)
    
 
if __name__ == '__main__':
    main()
