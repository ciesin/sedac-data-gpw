import os
import multiprocessing
import arcpy

def fixNames(gdb):
    arcpy.env.workspace = gdb
    stateCode = os.path.basename(gdb).split("_")[1][:2].upper()
    nameTable = r'H:\gpw\names_to_fix.gdb' + os.sep + stateCode + "_names"
    totRaw = arcpy.ListTables("*total_pop_raw")[0]
    sexRaw = arcpy.ListTables("*sex_variables_raw")[0]
    totIn = arcpy.ListTables("*total_pop_input")[0]
    sexIn = arcpy.ListTables("*sex_variables_input")[0]
    totEst = arcpy.ListTables("*total_pop_estimates")[0]
##    sexEst = arcpy.ListTables("*sex_variables_proportions")[0]
    
    #Make dictionaries of names
    dict2 = {}
    dict3 = {}
    dict4 = {}
    with arcpy.da.SearchCursor(nameTable,['UBID','NAME4','NAME3','NAME2']) as cursor:
        for row in cursor:
            dict2[row[0]]=row[3]
            dict3[row[0]]=row[2]
            dict4[row[0]]=row[1]


   
    tbls = [totRaw,sexRaw,totIn,sexIn,totEst]#,sexEst]
    for tbl in tbls:
##        arcpy.CalculateField_management(tbl,"NAME5",
##                                        '"Block "' + "!UCADMIN5!","PYTHON")
        #Update name tables with dictionaries
        with arcpy.da.UpdateCursor(tbl,['UBID','NAME2','NAME3','NAME4','NAME5',"UCADMIN5"]) as cursor:
            for row in cursor:
                UBID = row[0]
                row[1]=dict2[UBID]
                row[2]=dict3[UBID]
                row[3]=dict4[UBID]
                row[4]="Block " + str(row[5])
                cursor.updateRow(row)
        

    return "processed " + stateCode   

def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'H:\gpw\stage'
    workspaces = [workspace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt) 
    for gdbItem in gdb_list:
        print fixNames(gdbItem)
##    print len(gdb_list)
##    pool = multiprocessing.Pool(processes=15,maxtasksperchild=1)
##    try:
##        print pool.map(fixNames, gdb_list)
##        # Synchronize the main process with the job processes to
##        # ensure proper cleanup.
##        pool.close()
##        pool.join()
##    except:
##        print sys.stdout
##        pool.close()
##        pool.join()
        
    # End main
    
 
if __name__ == '__main__':
    main()
