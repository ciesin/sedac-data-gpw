# multiprocess template
import os, datetime, zipfile
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(params):
    processTime = datetime.datetime.now()
    try:
        zipList = params[0]
        outZip = params[1]
        zf = zipfile.ZipFile(outZip,mode='w')
        for z in zipList:
            zf.write(z,os.path.basename(z),compress_type=zipfile.ZIP_DEFLATED)
        zf.close()
        del zf
        return "Processed "+ outZip + " " + str(datetime.datetime.now()-processTime)
    except:
        return "Error while processing " + outZip + " " + str(datetime.datetime.now()-processTime)
    
def main():
    workspace = r'F:\gpw\ascii'
    arcpy.env.workspace = workspace
    zipWS = workspace+"_zips"
    print "processing"
    rasters = arcpy.ListRasters("*e_*totpopbt*sec_1*")
    rasters.sort()
    # must create procList
    procList=[]
    tileList=["_1.","_2.","_3.","_4.","_5.","_6.","_7.","_8."]
    for r in rasters:
        for tile in tileList:
            if tile == tileList[0]:
                raster = r
            else:
                raster = r.replace("_1.",tile)
            bt = os.path.join(workspace,raster)
            if tile == tileList[0]:
                zipList = [bt]
            else:
                zipList = zipList + [bt]
        prjList = []
        for z in zipList:
            prjList.append(z.replace(".asc",".prj"))
        zipList = zipList + prjList
        outZip = zipWS + os.sep + raster.replace("_8.",".") +".zip"
        procList.append((zipList,outZip))
    print len(procList)
    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
