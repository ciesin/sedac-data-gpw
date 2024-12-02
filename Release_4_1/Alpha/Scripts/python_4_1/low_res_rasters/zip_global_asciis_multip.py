#Jane Mills
#7/13/2017
#zip all global ascii files

import zipfile, os, datetime, re, multiprocessing
startTime = datetime.datetime.now()

def make_zip(r):
    outFolder = r'F:\gpw\ascii_zips'
    inFolder = r'F:\gpw\ascii'
    asciiList = os.listdir(inFolder)
    resList = ["30_sec","2pt5_min","15_min","30_min","1_deg"]
    os.chdir(inFolder)
    returnList = []

    for res in resList:
        outZip = os.path.join(outFolder,r+"_"+res+"_ascii.zip")
        if os.path.exists(outZip):
            returnList.append("Already zipped: " + r)
        else:
            zipFile = zipfile.ZipFile(outZip,'w', zipfile.ZIP_DEFLATED)
            fileList = filter(lambda x: r in x and (res in x or "lookup" in x), asciiList)
            for f in fileList:
                zipFile.write(f)

            zipFile.close()
    returnList.append("Zipped: " + r)
    
def main():
    tifFolder = r'D:\gpw\release_4_1\gdal_tifs'
    print "processing"

    rList1 = os.listdir(tifFolder)
    rList = [r[:-11] for r in filter(lambda x: "30_sec" in x and x[-3:] == "tif", rList1)]
    rList.sort()

    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(make_zip, rList)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-startTime)


if __name__ == '__main__':
    main()
