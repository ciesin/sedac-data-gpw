# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
arcpy.CheckOutExtension('SPATIAL')
# read the nid code dictionary
nidCodeDict = {}
with arcpy.da.SearchCursor(r'D:\gpw\ancillary.gdb\gpw4_country_codes',['ISO','UCADMIN0']) as rows:
    for row in rows:
        nidCodeDict[row[0]]=row[1]        
# copy the global raster into global memory
maxAreaIn = r'D:\gpw\release_4_1\national_identifier_grid\gpw_v4_maskedareakm_max.tif'
maxAreaInMem = 'in_memory' + os.sep + 'maxarea'
arcpy.CopyRaster_management(maxAreaIn,maxAreaInMem)

def process(raster):
    processTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    try:
        iso = os.path.basename(raster)[:3]
        # look up the nid code
        nid = nidCodeDict[iso]
        maxArea = arcpy.Raster(maxAreaInMem)      
        outRaster = os.path.dirname(raster) + os.sep + os.path.basename(raster).replace("MASKEDAREAKM","NATIONAL_IDENTIFIER")
        raster = arcpy.Raster(raster)
        conRaster = arcpy.sa.Con((raster - maxArea)==0,nid)
        arcpy.env.compression = 'LZW'
        arcpy.CopyRaster_management(conRaster,outRaster)
        return "Processed " + iso + " " + str(datetime.datetime.now()-processTime)
    except:
        return "Error while processing " + iso + " " + str(datetime.datetime.now()-processTime) + " " + arcpy.GetMessages()
    

def main():
    workspace = r'D:\gpw\release_4_1\country_tifs'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    procList = []
    folders = arcpy.ListWorkspaces("*")
    for folder in folders:
        if os.path.basename(folder) == 'cas' or os.path.basename(folder) == 'bla':
            continue
        arcpy.env.workspace = folder
        subfolders = arcpy.ListWorkspaces("**")
        if len(subfolders) == 0:
            raster = arcpy.ListRasters("*maskedareakm*")[0]
            procList.append(os.path.join(folder,raster))
        else:
            for subfolder in subfolders:
                arcpy.env.workspace = subfolder
                raster = arcpy.ListRasters("*maskedareakm*")[0]
                procList.append(os.path.join(subfolder,raster))
    for p in procList:
        print process(p)
##    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
##    results = pool.map(process, procList)
##    for result in results:
##        print result
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
