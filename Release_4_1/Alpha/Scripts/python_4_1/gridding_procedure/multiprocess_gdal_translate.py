# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(sourcefile):
    sourceRoot = os.path.basename(sourcefile)
    datasetName = sourceRoot#.replace('.tif','_30_sec.tif')
    tifsFolder = r'D:\gpw\release_4_1\gdal_tifs'  
    destinationfile = os.path.join(tifsFolder,datasetName)
    if not arcpy.Exists(destinationfile):
##        os.system("gdal_translate -ot Float32 -co COMPRESS=LZW -of GTiff " + sourcefile + " " +  destinationfile)
        os.system("gdal_translate -ot Int16 -co COMPRESS=LZW -of GTiff " + sourcefile + " " +  destinationfile)
##        os.system("gdal_translate -ot Byte -co COMPRESS=LZW -of GTiff " + sourcefile + " " +  destinationfile)
##    arcpy.BuildPyramidsandStatistics_management(destinationfile)
##    arcpy.Delete_management(sourcefile)
    return destinationfile
def main():
##    workspace = r'D:\gpw\release_4_1\merge'
    workspace = r'D:\gpw\release_4_1\low_res'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    procList = [os.path.join(workspace,raster) for raster in arcpy.ListRasters("*national*")]#arcpy.ListRasters("*cntm*")+arcpy.ListRasters("*dens*")]                       
    print procList
    pool = multiprocessing.Pool(processes=4,maxtasksperchild=1)
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
