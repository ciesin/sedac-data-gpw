import arcpy, os, multiprocessing, datetime
arcpy.CheckOutExtension('Spatial')

def process(mosaicList):
    print mosaicList
    variable = os.path.basename(mosaicList[0])[3:]
    print variable
    outGDB = r'D:\gpw\4_0_prod\mosaics.gdb'
    if os.path.basename(os.path.dirname(os.path.dirname(mosaicList[0])))=='prod_countries':
        outName = 'prod' + variable
    else:
        outName = 'beta' + variable
    arcpy.env.cellSize = mosaicList[0]
    arcpy.env.extent = r'D:\gpw\4_0_prod\gpw-v4-land-water-area\gpw-v4-land-water-area_land.tif'
    WGS84 = arcpy.SpatialReference(4326)
    try:
        arcpy.MosaicToNewRaster_management(mosaicList,outGDB,outName,WGS84,
                                           '32_BIT_FLOAT','#',1,'FIRST','FIRST')
        return "CREATED MOSAIC" + outName
    except:
        return arcpy.GetMessages()
def main():
    scriptTime = datetime.datetime.now()
    masterList = []
    
    arcpy.env.workspace = r'D:\gpw\4_0_prod\prod_countries'
    gdbs = arcpy.ListWorkspaces("*")
    arcpy.env.workspace = r'D:\gpw\4_0_prod\beta_countries'
    gdbs2 = arcpy.ListWorkspaces("*")
    for gdb in gdbs:
        arcpy.env.workspace = gdb
        raster1 = []#arcpy.ListRasters("*_AREA*")
        raster2 = []#arcpy.ListRasters("*WATER*")
        raster3 = arcpy.ListRasters("*_UNE_*BT*")
        rasters = raster1 + raster2 + raster3
        for raster in rasters:
            variable = raster[3:]
            l1 = [gdb + os.sep + os.path.basename(gdb)[:-4].upper() + variable for gdb in gdbs]
            l2 = [gdb + os.sep + os.path.basename(gdb)[:-4].upper() + variable for gdb in gdbs2]
            masterList.append(l1)
            masterList.append(l2)
        break

    for x in masterList:
        print process(x)
    # multiprocess the data
##    pool = multiprocessing.Pool(processes=18,maxtasksperchild=1)
##    print pool.map(process, masterList) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)
    
if __name__ == '__main__':
    main()
