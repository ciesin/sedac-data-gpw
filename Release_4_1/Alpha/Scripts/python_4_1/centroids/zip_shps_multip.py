#Jane Mills
#7/13/2017
#zip all shapefiles

import arcpy, zipfile, os, datetime, re, multiprocessing
startTime = datetime.datetime.now()

def make_zip(iso):
    root = r'D:\gpw\release_4_1\centroids'
    shpFolder = os.path.join(root,'shp')
    zipFolder = os.path.join(root,'zip')

    os.chdir(shpFolder)
    fileList = os.listdir(shpFolder)
    returnList = []

    subList = filter(lambda x: iso == x[:len(iso)], fileList)

    outZip = os.path.join(zipFolder,iso+'_centroids.shp.zip')
    if os.path.exists(outZip):
        returnList.append("Already zipped: " + iso)
    else:
        zipFile = zipfile.ZipFile(outZip,'w', zipfile.ZIP_DEFLATED)
        for f in subList:
            zipFile.write(f)

        zipFile.close()
        returnList.append("Zipped: " + iso)
    
def main():
    root = r'D:\gpw\release_4_1\centroids'
    shpFolder = os.path.join(root,'shp')
    print "processing"

    arcpy.env.workspace = shpFolder
    list1 = [fc.split("_")[0] for fc in arcpy.ListFeatureClasses()]
    isoList = list(set(list1))
    isoList.sort()

    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(make_zip, isoList)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-startTime)


if __name__ == '__main__':
    main()
