#Jane Mills
#GPW
#Aggregate

import arcpy, os, multiprocessing
from arcpy import env
from arcpy.sa import *

def dens(rPath):
    r = os.path.basename(rPath)
    arcpy.CheckOutExtension("Spatial")
    env.overwriteOutput = True
    env.scratchWorkspace = r'F:\gpw\v411\scratch'
    env.compression = "LZW"
    outFolder = r'F:\gpw\v411\rasters_lower_resolution'
    returnList = None
    
    try:
        res = "_".join(r[:-4].split("_")[-2:])
        areaRast = os.path.join(outFolder,'gpw_v4_land_water_area_rev11_landareakm_'+res+'.tif')

        outR = os.path.join(outFolder,r.replace("cntm","dens").replace("count_","density_"))
        #outDivide = Divide(rPath, areaRast)
        outDivide = Con(Raster(rPath) == 0, 0, Raster(rPath)/Raster(areaRast))
        arcpy.CopyRaster_management(outDivide,outR)
    
        returnList = "Succeeded " + r
    except:
        returnList = "Failed " + r
    return returnList


def main():
    root = r'F:\gpw\v411\rasters_lower_resolution'
    env.workspace = root
    allRasters = arcpy.ListRasters()

    rList1 = arcpy.ListRasters("*demographic*cntm*") + arcpy.ListRasters("*population_count*")
    rList = [os.path.join(root,r) for r in rList1 if not r.replace("cntm","dens").replace("count_","density_") in allRasters]
    rList.sort()
    
    print("Processing {} rasters".format(len(rList)))

    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(dens, rList)
    for result in results:
        print(result)

    pool.close()
    pool.join()
    print("Script complete")


if __name__ == '__main__':
    main()


