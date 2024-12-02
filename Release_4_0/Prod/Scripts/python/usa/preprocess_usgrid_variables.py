# create input usgrids tables
# this script has custom considerations that may make it difficult to reuse in its entirety
# however there may be useful snippets for reuse
# Kytt MacManus

import arcpy, os, sys, datetime, multiprocessing

def copyTables(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[4:6]
    # sf1tables
    inputTable = r'H:\gpw\sf1_tables_final.gdb' + os.sep + iso + '_variable_inputs'
    # first deal with the pop data
    popTable = gdb + os.sep + 'usa_' + iso + '_admin5_2010_usgrids_pop_input'
    # if the table exists exit
    if arcpy.Exists(popTable):
        return iso + " was already processed"
    popFields = ["POP","WHITE","BLACK","AMIND","ASIAN","HAWPI","HISP","P25","AUND1",
                 "A1TO4","A5TO17","A18TO24","A25TO64","A65TO79","AOV80","HHP","NHWHITE",
                 "NHBLACK","PUND25","OTHER","TWOMORE","NHISP"]
    # next the hh data
    hhTable = gdb + os.sep + 'usa_' + iso + '_admin5_2010_usgrids_hh_input'
    hhFields = ["HH","HHP","FEM","HU","OCC","OWN","SEA","HU1P"]
    tables = [popTable,hhTable]
    for table in tables:
        if table == popTable:
            fields = hhFields
        else:
            fields = popFields
        arcpy.CopyRows_management(inputTable,table)
        for field in fields:
            arcpy.DeleteField_management(table,field)
    # print total time to run
    return iso + ": " + str(datetime.datetime.now()-startTime)
    


def main():
    startTime = datetime.datetime.now()
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'H:\gpw\pop_tables' # on machine devsedarc2
    arcpy.env.workspace = workspace
    gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
    gdbs.sort()
    gdb_list = [os.path.join(workspace, gdb) for gdb in gdbs]
    print len(gdb_list)
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
    try:
        print pool.map(copyTables, gdb_list)
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool.close()
        pool.join()
    except:
        print sys.stdout
        pool.close()
        pool.join()
    # End main
    print "Script Complete: " + str(datetime.datetime.now()-startTime)
    
 
if __name__ == '__main__':
    main()
