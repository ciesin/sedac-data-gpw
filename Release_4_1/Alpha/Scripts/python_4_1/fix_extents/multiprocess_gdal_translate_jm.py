# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(sourcefile):
    sourceRoot = os.path.basename(sourcefile)
    datasetName = sourceRoot
    tifsFolder = r'F:\gpw\gpw4_rev10_fixed_extents\gdal_tifs'  
    destinationfile = os.path.join(tifsFolder,datasetName)
    if not arcpy.Exists(destinationfile):
        if "context" in datasetName or "watermask" in datasetName:
            os.system("gdal_translate -ot Byte -co COMPRESS=LZW -of GTiff " + sourcefile + " " +  destinationfile)
        elif "identifier" in datasetName:
            os.system("gdal_translate -ot Int16 -co COMPRESS=LZW -of GTiff " + sourcefile + " " +  destinationfile)
        else:
            os.system("gdal_translate -ot Float32 -co COMPRESS=LZW -of GTiff " + sourcefile + " " +  destinationfile)
        return datasetName
def main():
##    workspace = r'D:\gpw\release_4_1\merge'
    workspace = r'F:\gpw\gpw4_rev10_fixed_extents\rasters'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    procList = [os.path.join(workspace,raster) for raster in arcpy.ListRasters("*_une_*")]
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

