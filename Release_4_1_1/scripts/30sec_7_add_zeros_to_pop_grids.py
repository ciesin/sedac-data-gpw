# Jane Mills
# Put zeros back into pop grids

import arcpy, os, multiprocessing
from arcpy.sa import *
arcpy.env.overwriteOutput = True

def process(r):
    message = None
    
    rbase = os.path.basename(r)
    outFolder = r'F:\gpw\v411\rasters_30sec_fixed_zeros'
    outRaster = os.path.join(outFolder,rbase.replace("rev10","rev11"))
    
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.scratchWorkspace = r'F:\gpw\v411\scratch'
    arcpy.env.compression = "LZW"
    
    if "demographic" in rbase and "atotpopbt" not in rbase:
        mask = Raster(r'F:\gpw\v411\masks\demographic_mask.tif')
        arcpy.env.extent = arcpy.Describe(mask).Extent
        
        try:
            outCon = Con(IsNull(Raster(r)) == 0, Raster(r), Con(mask != -1, 0))
            arcpy.CopyRaster_management(outCon, outRaster)
            message = "Succeeded: " + rbase
        except:
            message = "Failed: " + rbase
        
    if "population" in rbase or "atotpopbt" in rbase:
        mask = Raster(r'F:\gpw\v411\masks\pop_mask.tif')
        arcpy.env.extent = arcpy.Describe(mask).Extent
        try:
            outCon = Con((mask==0) & (IsNull(Raster(r))==1), 0, Raster(r))
            arcpy.CopyRaster_management(outCon,outRaster)
            message = "Succeeded: " + rbase
        except:
            message = "Failed: " + rbase
    
    return message
    
def main():
    inFolder = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters'
    outFolder = r'F:\gpw\v411\rasters_30sec_fixed_zeros'

    arcpy.env.workspace = outFolder
    outRasters = arcpy.ListRasters()

    arcpy.env.workspace = inFolder
    inRasters = arcpy.ListRasters("*demographic*30_sec*") + arcpy.ListRasters("*population*30_sec*")
    inRasters.sort()
    rasterList = [os.path.join(inFolder,r) for r in inRasters if r.replace("rev10","rev11") not in outRasters]
    
    print("Set up complete")
    
    pool = multiprocessing.Pool(processes=min([20,len(rasterList)]),maxtasksperchild=1)
    results = pool.map(process, rasterList)
    for result in results:
        print(result)
    pool.close()
    pool.join()

    print("Script complete")
    
if __name__ == '__main__':
    main()


