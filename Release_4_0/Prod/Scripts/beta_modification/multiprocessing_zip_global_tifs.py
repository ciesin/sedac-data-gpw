import zipfile, os, arcpy, glob, datetime, multiprocessing

def zipIt(folder):
    procTime = datetime.datetime.now()
    outputws = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters\global_zips'
    docws = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters\gpw-v4-documentation' ##UPDATE
    # set os cwd and arcpy workspace
    os.chdir(folder)
    arcpy.env.workspace = folder
    rasters = arcpy.ListRasters("*")
    # first zip each raster individually
    combinedList = []
    for raster in rasters:
        # create zipFile
        outZip = outputws + os.sep + raster.replace('tif','zip').replace('_','-')
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
                
    return (folder,str(datetime.datetime.now() - procTime))


def main():
    scriptTime = datetime.datetime.now()
    datadir = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\rasters\global_tifs'
    arcpy.env.workspace = datadir
    folders = arcpy.ListWorkspaces("*","Folder")
    
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=7,maxtasksperchild=1)
    results = pool.map(zipIt, folders)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
