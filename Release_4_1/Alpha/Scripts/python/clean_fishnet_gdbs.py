import arcpy, os, multiprocessing

def cleanFishnets(gdb):
    arcpy.env.workspace = gdb
    fcs = arcpy.ListFeatureClasses("*")
    tbls = arcpy.ListTables("*")
    combined = fcs + tbls
    for ds in combined:
        if ds[-7:]=='fishnet':
            pass
        else:
            arcpy.Delete_management(ds)
    return "Cleaned " + gdb 

def main():
    scriptTime = datetime.datetime.now()
    arcpy.env.workspace = r'D:\gpw\stage\fishnets'
    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    try:
        print pool.map(cleanFishnets, gdbs)
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool.close()
        pool.join()
    except:
        print sys.stdout
        pool.close()
        pool.join()

    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
