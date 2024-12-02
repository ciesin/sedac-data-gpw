# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(sourcefile):
    datasetName = os.path.basename(sourcefile)
    tifsFolder = r'D:\gpw\release_4_1\global_gdal_tifs'
    destinationfile = os.path.join(tifsFolder,datasetName)
    if not arcpy.Exists(destinationfile):
        os.system("gdal_translate -ot float32 -co COMPRESS=LZW -of GTiff " + sourcefile + " " +  destinationfile)

    return datasetName
def main():
##    workspace = r'D:\gpw\release_4_1\merge'
    workspace = r'D:\gpw\release_4_1\global_tifs'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    procList = [os.path.join(workspace,r) for r in arcpy.ListRasters()]
    #print procList
    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
