import zipfile, os, datetime, arcpy
startTime = datetime.datetime.now()
tifFolder = r'D:\gpw\release_4_1\gdal_tifs'
inFolder = r'F:\gpw\ascii'
outFolder = r'F:\gpw\ascii_zips'

arcpy.env.workspace = tifFolder
rList = [r[:-11] for r in arcpy.ListRasters("*30_sec*")]
resList = ["30_sec","2pt5_min","15_min","30_min","1_deg"]
asciiList = os.listdir(inFolder)
os.chdir(inFolder)

for r in rList:
    print r
    for res in resList:
        outZip = os.path.join(outFolder,r+"_"+res+"_ascii.zip")
        if arcpy.Exists(outZip):
            print outZip + " already exists"
        else:
            zipFile = zipfile.ZipFile(outZip,'w', zipfile.ZIP_DEFLATED,allowZip64 = True)
            fileList = filter(lambda x: r in x and (res in x or "lookup" in x), asciiList)
            for f in fileList:
                zipFile.write(f)

            zipFile.close()
    print "Created: " + r

print "Script Complete: " + str(datetime.datetime.now() - startTime)
    
