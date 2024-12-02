import os, arcpy, datetime, multiprocessing

def dissolve(f):
    procTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    outFile=r'D:\gpw\boundaries_used_for_gridding_dissolved'+ os.sep + os.path.basename(f)+"_dissolve.shp"
    arcpy.Dissolve_management(f,outFile)
    return (outFile,str(datetime.datetime.now() - procTime))


def main():
    
    scriptTime = datetime.datetime.now()
    datadir = r'D:\gpw\us_boundaries_hi_res.gdb'
    arcpy.env.workspace = datadir
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.join(datadir,f) for f in fcs]
    
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=18,maxtasksperchild=1)
    results = pool.map(dissolve, fcList)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
