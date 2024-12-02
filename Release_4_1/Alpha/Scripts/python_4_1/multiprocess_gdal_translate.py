# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(sourcefile):
    sourceRoot = os.path.basename(sourcefile)
##    split = sourceRoot.split("_")
##    # parse for an output name
##    if split[2][:1]=='u':
##        if split[-1]=='dens.tif':
##            shuid = r'gpw-v4-population-density-adjusted-to-2015-unwpp-country-totals-rev10'
##            year = split[-2]
##        else:
##            shuid = r'gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals-rev10'
##            year = split[-1][:-4]
##        datasetName = shuid + '-' + year + '-30-sec.tif'
##    
##    elif split[2][:1]=='t':
##        if split[-1]=='dens.tif':
##            shuid = r'gpw-v4-population-density-rev10'
##            year = split[-2]
##        else:
##            shuid = r'gpw-v4-population-count-rev10'
##            year = split[-1][:-4]
##        datasetName = shuid + '-' + year + '-30-sec.tif'
##    else:
##        if split[-1]=='dens.tif':
##            shuid = r'gpw-v4-basic-demographic-characteristics-density-rev10'
##            if len(split)==5:
##                age = split[2]
##            else:
##                age = split[2]+"-"+split[3]
##        else:
##            shuid = r'gpw-v4-basic-demographic-characteristics-count-rev10'
##            if len(split)==4:
##                age = split[2]
##            else:
##                age = split[2]+"-"+split[3]
##            year = split[-1][:-4]
##        datasetName = shuid + '-' + age + '-2010-30-sec.tif'
    datasetName = sourceRoot
        
    tifsFolder = r'D:\gpw\release_4_1\gdal_tifs'  
    destinationfile = os.path.join(tifsFolder,datasetName)
    if not arcpy.Exists(destinationfile):
        os.system("gdal_translate -ot Float32 -co COMPRESS=LZW -of GTiff " + sourcefile + " " +  destinationfile)
##    arcpy.BuildPyramidsandStatistics_management(destinationfile)
##    arcpy.Delete_management(sourcefile)
    return destinationfile
def main():
    workspace = r'D:\gpw\release_4_1\low_res'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    procList = [os.path.join(workspace,raster) for raster in arcpy.ListRasters("*atotpopbt*2010*1_deg*")]                       
    print procList
    pool = multiprocessing.Pool(processes=2,maxtasksperchild=1)
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
