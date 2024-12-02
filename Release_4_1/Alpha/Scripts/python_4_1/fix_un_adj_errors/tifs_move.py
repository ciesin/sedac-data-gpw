#Jane Mills
#11/30/17
#Move incorrect UN adjusted tifs to another location on devsedarc4

# Import Libraries
import arcpy, os, shutil

root = r'D:\gpw\release_4_1\country_tifs'
outRoot = r'D:\gpw\release_4_1\country_tifs_wrong_adj'

isoList = ['blr','bra','chl','cpv','cub','cyp','ggy','jey','lao','lca','mmr','phl','prk','sau','ssd','uga']

folderList = os.listdir(root)
folderList.sort()

for iso in isoList:
    print iso
    inFolder = os.path.join(root,iso)

    outFolder = os.path.join(outRoot,iso)
    os.mkdir(outFolder)

    if iso == "bra":
        subFolders = os.listdir(inFolder)
        for sub in subFolders:
            print sub
            subPath = os.path.join(inFolder,sub)
            files = os.listdir(subPath)
            filesToMove = filter(lambda f: "UNE_ATOTPOPBT" in f, files)

            outSubFolder = os.path.join(outFolder,sub)
            os.mkdir(outSubFolder)

            for f in filesToMove:
                srcFile = os.path.join(subPath,f)
                dstFile = os.path.join(outSubFolder,f)
                shutil.copyfile(srcFile, dstFile)
                os.remove(srcFile)

            print "Moved " + str(len(filesToMove)) + " files"

    else:
        files = os.listdir(inFolder)
        filesToMove = filter(lambda f: "UNE_ATOTPOPBT" in f, files)

        for f in filesToMove:
            srcFile = os.path.join(inFolder,f)
            dstFile = os.path.join(outFolder,f)
            shutil.copyfile(srcFile, dstFile)
            os.remove(srcFile)

        print "Moved " + str(len(filesToMove)) + " files"


print 'done'
