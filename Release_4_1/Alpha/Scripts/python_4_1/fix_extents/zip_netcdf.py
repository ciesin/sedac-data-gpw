#Jane Mills
#7/13/2017
#zip all global netcdf files

import zipfile, os, datetime, re, multiprocessing, csv, shutil
startTime = datetime.datetime.now()

def make_zip(z):
    returnList = []

    readme = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\fix_extents\text_files\readme.txt'
    outFolder = r'F:\gpw\gpw4_rev10_fixed_extents\zipped_netcdf'
    inFolder = r'F:\gpw\gpw4_rev10_fixed_extents\netcdf'
    
    outZipName = z[0]
    readmeName = outZipName[:-4].replace("-","_") + "_readme.txt"
    lookups = ["gpw_v4_netcdf_contents.csv","gpw_v4_context_lookup.txt",
               "gpw_v4_data_type_lookup.txt","gpw_v4_national_identifier_lookup.txt"]
    fileList = z[1:]
    os.chdir(inFolder)

    outReadme = os.path.join(inFolder,readmeName)
    outZip = os.path.join(outFolder,outZipName)
    if os.path.exists(outZip):
        returnList.append("Already zipped: " + outZipName)
    else:
        shutil.copy(readme,outReadme)
        zipFile = zipfile.ZipFile(outZip,'w', zipfile.ZIP_DEFLATED,allowZip64 = True)
        for f in fileList + lookups:
            zipFile.write(f)

        zipFile.write(readmeName)
        zipFile.close()

        os.remove(outReadme)

        returnList.append("Zipped: " + outZipName)
    return returnList
    
def main():
    print "processing"

    zipcsv = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\fix_extents\zips_netcdf.csv'
    csvMem = csv.reader(open(zipcsv,'r'))
    next(csvMem)
    nameDict = {}
    zipList = []

    for row in csvMem:
        if not row[1] in nameDict:
            nameDict[row[1]] = [row[0]]
        else:
            nameDict[row[1]] += [row[0]]

    for key in nameDict:
        zipList.append([key]+nameDict[key])

    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(make_zip, zipList)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-startTime)


if __name__ == '__main__':
    main()
