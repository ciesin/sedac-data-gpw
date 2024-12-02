import zipfile, os, arcpy, glob, datetime
startTime = datetime.datetime.now()
datadir = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters\global_tifs'
outputws = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters\global_zips'
# change os working directory to the input file location, otherwise the
# zipfile recreates the complete path within the archive.
# define doc variabls
docws = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters\gpw-v4-documentation' ##UPDATE
arcpy.env.workspace = datadir
workspaces = arcpy.ListWorkspaces("*","Folder")
for folder in workspaces:
    print folder
    # set os cwd and arcpy workspace
    os.chdir(folder)
    arcpy.env.workspace = folder
    rasters = arcpy.ListRasters("*")
    # first zip each raster individually
    combinedList = []
    for raster in rasters:
        procTime = datetime.datetime.now()
        # create zipFile
        outZip = outputws + os.sep + raster.replace('.tif','.zip').replace('_','-')
        if arcpy.Exists(outZip):
            print outZip + " already exists"
        else:
            zipFile = zipfile.ZipFile(outZip,'w', zipfile.ZIP_DEFLATED)
            # add documentation
            os.chdir(docws)
            dnames = glob.glob("*")
            for d in dnames:
                zipFile.write(d)
            os.chdir(folder)
            # glob the files that match the raster wildcard
            wildcard = raster[:-4]
            fnames = glob.glob(wildcard + "*")
            for f in fnames:
                if f[-4:]=="lock":
                    continue
                
                combinedList.append(f)
                zipFile.write(f)
            zipFile.close()
            print "Created " + outZip
            print datetime.datetime.now() - procTime
print "Script Complete: " + str(datetime.datetime.now() - startTime)
    


