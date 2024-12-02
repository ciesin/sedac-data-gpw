import zipfile, os, arcpy, glob, datetime
startTime = datetime.datetime.now()
datadir = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters_lower_resolution\global_data'
outputws = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters_lower_resolution\global_zips'
# change os working directory to the input file location, otherwise the
# zipfile recreates the complete path within the archive.
# define doc variables
docws = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters_lower_resolution\gpw-v4-documentation' ##UPDATE
arcpy.env.workspace = datadir
workspaces = arcpy.ListWorkspaces("*","Folder")
for folder in workspaces:
    print folder
    if folder[-5:] == 'ascii' and 'national-identifier' in folder:
        # set os cwd and arcpy workspace
        inFolder = os.path.join(datadir,folder)
        os.chdir(folder)
        asciis = os.listdir(inFolder)
        # first zip each raster individually
        combinedList = []
        ascii = asciis[0]
        procTime = datetime.datetime.now()
        # create zipFile
        outZip = outputws + os.sep + ascii.replace('.txt','-ascii.zip').replace('_','-')
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
            wildcard = ascii[:-4]
            fnames = glob.glob(wildcard + "*")
            f = fnames[0]
            combinedList.append(f)
            zipFile.write(f)
            zipFile.close()
            print "Created " + outZip
            print datetime.datetime.now() - procTime

print "Script Complete: " + str(datetime.datetime.now() - startTime)
    
