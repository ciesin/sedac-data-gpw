# Jane Mills
# 10/31/2018
# zip everything

import zipfile, os, csv, multiprocessing, shutil

def zipFiles(zipSetUp):
    message = None
    
    zipFolder = r'F:\gpwv411\zips'    
    outZip = zipSetUp[0]
    outZipName = os.path.basename(outZip)
    fileList = zipSetUp[1]
    
    try:
        lookupFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\netCDF\lookups'
        readMeOrig = r'\\Dataserver1\gpw\GPW4\Release_411\documentation\zipFile_readme.txt'
        readmeName = outZipName[:-4].replace("-","_") + "_readme.txt"
        outReadme = os.path.join(zipFolder,readmeName)
        shutil.copy(readMeOrig,outReadme)
        
        lookupList = []
        
        if outZipName[-7:] == "_nc.zip":
            lookupList = [os.path.join(lookupFolder,f) for f in os.listdir(lookupFolder) if f[-5:] != ".xlsx"]
        if outZipName[-8:] == "_asc.zip" and "watermask" in outZipName:
            lookupList = [os.path.join(lookupFolder,f) for f in os.listdir(lookupFolder) if "water" in f]
        if outZipName[-8:] == "_asc.zip" and "context" in outZipName:
            lookupList = [os.path.join(lookupFolder,f) for f in os.listdir(lookupFolder) if "context" in f]
        if outZipName[-8:] == "_asc.zip" and "identifier" in outZipName:
            lookupList = [os.path.join(lookupFolder,f) for f in os.listdir(lookupFolder) if "identifier" in f]
            
        zipList = fileList + lookupList + [outReadme]
        zipFile = zipfile.ZipFile(outZip,'w', zipfile.ZIP_DEFLATED,allowZip64 = True)
        for z in zipList:
            zipFile.write(z, os.path.basename(z))
        zipFile.close()
        
        os.remove(outReadme)
        message = "Succeeded: " + os.path.basename(outZip)
        
    except:
        message = "Failed: " + os.path.basename(outZip)
        
    return message


##############################################################################################

def main():
    zipCSV = r'\\Dataserver1\gpw\GPW4\Release_411\ancillary\zipList.csv'
    zipFolder = r'F:\gpwv411\zips'
    
    zipDict = {}
    zipList = []
        
    with open(zipCSV,mode = "r") as openCSV:
        reader = csv.reader(openCSV)
        next(openCSV)
        for row in reader:
            if not row[2] in zipDict:
                zipDict[row[2]] = [row[1],[row[0]]]
            else:
                zipDict[row[2]][1] += [row[0]]
    
    for key in zipDict:
        outFolder = os.path.join(zipFolder,zipDict[key][0])
        if not os.path.exists(outFolder):
            os.mkdir(outFolder)
        
        outZip = os.path.join(outFolder,key)
        fileList = zipDict[key][1]
        if not os.path.exists(outZip):
            zipList.append([outZip, fileList])
            
    zipList.sort()
    
    print("Processing {} files".format(len(zipList)))
    
    pool = multiprocessing.Pool(processes=min([30,len(zipList)]),maxtasksperchild=1)
    results = pool.map(zipFiles, zipList)
    for result in results:
        print(result)
    pool.close()
    pool.join()

    print("Script complete")

##############################################################################################

if __name__ == '__main__':
    main()

