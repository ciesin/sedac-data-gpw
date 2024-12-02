import os
import multiprocessing
import arcpy

def fixNames(gdb):
    stateCode = os.path.basename(gdb).split("_")[1][:2].upper()
    nameTable = r'F:\usa\names_to_fix.gdb' + os.sep + stateCode + "_names"
    nameView = stateCode
    arcpy.MakeTableView_management(nameTable,nameView)
    arcpy.env.workspace = gdb
    totRaw = arcpy.ListTables("*total_pop_raw")[0]
    sexRaw = arcpy.ListTables("*sex_variables_raw")[0]
##    totIn = arcpy.ListTables("*total_pop_input")[0]
##    sexIn = arcpy.ListTables("*sex_variables_input")[0]
##    totEst = arcpy.ListTables("*total_pop_estimates")[0]
##    sexEst = arcpy.ListTables("*sex_variables_proportions")[0]
   
    tbls = [totRaw,sexRaw]#,totIn,sexIn,totEst,sexEst]
    for tbl in tbls:
        tblView = tbl + "_view"
        arcpy.MakeTableView_management(tbl,tblView)
        arcpy.CalculateField_management(tblView,"NAME5",
                                        '"Block "' + "!UCADMIN5!","PYTHON")
        arcpy.AddJoin_management(tblView,"UBID",nameView,"UBID")
        flds = ["NAME2","NAME3","NAME4"]
        for fld in flds:
            calcField = os.path.basename(tbl) + "." + fld
            expression = '!' + os.path.basename(nameTable) + "." + fld + '!'
            arcpy.CalculateField_management(tblView,calcField,expression,"PYTHON")

    return "processed " + stateCode   

def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'F:\usa\names'
    workspaces = [workspace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt) 
##    for gdbItem in gdb_list:
##        print fixNames(gdbItem)
    print len(gdb_list)
    pool = multiprocessing.Pool(processes=15,maxtasksperchild=1)
    try:
        print pool.map(fixNames, gdb_list)
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool.close()
        pool.join()
    except:
        print sys.stdout
        pool.close()
        pool.join()
        
    # End main
    
 
if __name__ == '__main__':
    main()
