#Jane Mills
#10/03/17
#zip netCDF

import zipfile, os
root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\netCDF'
zips = os.path.join(root,'zips')
lookups = os.path.join(root,'lookups')

lookupList = os.listdir(lookups)
lookupList.sort()
lookupList = lookupList[2:]

os.chdir(root)

fileList = os.listdir(root)
fileList.sort()

for f in fileList:
    if f[-3:] == ".nc":
        print f
        zipList = lookupList+[f]
        outZip = os.path.join(zips,f+'.zip')
        zipFile = zipfile.ZipFile(outZip,'w', zipfile.ZIP_DEFLATED,allowZip64 = True)
        for z in zipList:
            zipFile.write(z)
        zipFile.close()
        print "zipped"
    else:
        pass


