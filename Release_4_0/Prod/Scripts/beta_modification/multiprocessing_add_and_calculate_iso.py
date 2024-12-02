import os, arcpy, datetime, multiprocessing

def calc(f):
    # simple function
    procTime = datetime.datetime.now()
    iso= os.path.basename(f)[:3]
    arcpy.AddField_management(f,"iso","TEXT","#","#",5)
    arcpy.CalculateField_management(f,"iso",'"'+iso+'"',"PYTHON")
    return (iso,str(datetime.datetime.now() - procTime),arcpy.GetMessages())


def main():
    
    scriptTime = datetime.datetime.now()
    datadir = r'D:\gpw\boundaries_used_for_gridding_dissolved'
    arcpy.env.workspace = datadir
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.join(datadir,f) for f in fcs]
    # create multi-process pool and execute tool
    # processes sets the number of processors to use
    # I have had problems with garbage collection in
    # the past so maxtasksperchild is set to ensure clean
    # up of each individual job
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
    results = pool.map(calc, fcList)
    print(results)
    # synchronize the main process with the job processes
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
