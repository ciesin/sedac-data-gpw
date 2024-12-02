import os
import multiprocessing
import arcpy

def deleteDSM(gdb):
    arcpy.env.workspace = gdb
    arcpy.env.overwriteOutput=True
    estimatesFile = ""
##    try:
##        estimatesFile = gdb + os.sep + str(arcpy.ListTables("*estimates")[0])
##        dsmField = arcpy.ListFields(estimatesFile,"*WOMCHILD*")[0]
##        with arcpy.da.SearchCursor(estimatesFile,"*") as sc:
##            for row in sc:
##                str(row)
##                break
##        return gdb
##    except:
##        # delete the table
##        if arcpy.Exists(estimatesFile):
##            arcpy.Delete_management(estimatesFile)
##        return "Error: " + gdb
##        # grab new estimates file and copy it over
##        newEstimatesGDB = r'H:\gpw\pop_tables' + os.sep + os.path.basename(gdb)
##        arcpy.env.workspace = newEstimatesGDB
##        newEstimatesFile = newEstimatesGDB + os.sep + str(arcpy.ListTables("*estimates")[0])
##        estimatesFile = newEstimatesFile.replace("pop_tables",r"stage/pop_tables")       
##        arcpy.CopyRows_management(newEstimatesFile,estimatesFile)
    estimatesFile = gdb + os.sep + str(arcpy.ListTables("*estimates")[0])
    fields = arcpy.ListFields(estimatesFile,"*DSM")
    if len(fields)>0:
        delFields = [f.name for f in fields]
        delFields.append("ADMINAREAKMMASKED")
        arcpy.DeleteField_management(estimatesFile,delFields)
        return "Deleted DSM fields in: " + gdb
    else:
        return "  DSM fields already deleted in: " + gdb
     

def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'H:\gpw\stage\pop_tables'
    arcpy.env.workspace = workspace
    gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
    gdbs.sort() 
    for gdb in gdbs:
####        if gdb == r'H:\gpw\stage\pop_tables\usa_al.gdb':
####            continue
        print gdb
        print deleteDSM(gdb)
##    print len(gdbs)
##    gdb_list = [r'H:\gpw\stage\pop_tables\usa_al.gdb',
##                r'H:\gpw\stage\pop_tables\usa_az.gdb',
##                r'H:\gpw\stage\pop_tables\usa_ia.gdb',
##                r'H:\gpw\stage\pop_tables\usa_id.gdb']
##    pool = multiprocessing.Pool(processes=4,maxtasksperchild=1)
##    try:
##        print pool.map(deleteDSM, gdb_list)
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
