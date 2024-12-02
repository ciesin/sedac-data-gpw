import os, arcpy, datetime, multiprocessing

def dissolve(f):
    procTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    outFile=r'D:\gpw\release_4_1\loading\admin0_shps'+ os.sep + os.path.basename(f)[:3]+"_admin0.shp"
    arcpy.Dissolve_management(f,outFile)
    arcpy.AddField_management(outFile,"iso","TEXT","#","#",5)
    arcpy.CalculateField_management(outFile,"iso",'"'+os.path.basename(f)[:3]+'"',"PYTHON")
    return (outFile,str(datetime.datetime.now() - procTime))


def main():
    
    scriptTime = datetime.datetime.now()
    datadir = r'D:\gpw\release_4_1\loading\hi_res_boundaries_10_20_16.gdb'
    arcpy.env.workspace = datadir
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.join(datadir,f) for f in fcs]
    
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
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
