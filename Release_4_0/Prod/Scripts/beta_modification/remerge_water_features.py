import os, arcpy, datetime, multiprocessing

def merge(f):
    procTime = datetime.datetime.now()
    arcpy.env.workspace = r'D:\gpw\country_boundaries_hi_res.gdb'
    f2 = arcpy.ListFeatureClasses(os.path.basename(f)[:3]+"*")[0]
    outFile=r'D:\gpw\water_merge.gdb'+ os.sep + os.path.basename(f)[:3]
    arcpy.Merge_management([f,f2],outFile)
    return (f,str(datetime.datetime.now() - procTime))


def main():
    scriptTime = datetime.datetime.now()
    datadir = r'Z:\GPW4\Release_4_0\Prod\Water_mask_changes\Boundary_water_features\boundary_water_features_NO_POP.gdb'
    arcpy.env.workspace = datadir
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.join(datadir,f) for f in fcs]
    
    # create multi-process pool and execute tool
    for f in fcList:
        print merge(f)
##    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
##    results = pool.map(merge, fcList)
##    print(results)
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
