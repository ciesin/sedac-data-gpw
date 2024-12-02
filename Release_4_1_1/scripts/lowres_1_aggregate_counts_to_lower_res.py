#Jane Mills
#GPW
#Aggregate

import arcpy, os, multiprocessing
from arcpy import env
from arcpy.sa import *

def aggregate_rasters(rPath):
    r = os.path.basename(rPath)
    arcpy.CheckOutExtension("Spatial")
    env.overwriteOutput = True
    env.scratchWorkspace = r'F:\gpw\v411\scratch'
    env.compression = "LZW"
    outFolder = r'F:\gpw\v411\rasters_lower_resolution'
    resolutions = ['2pt5_min','15_min','30_min','1_deg']
    scales = ['5','30','60','120']
    returnList = None
    
    try:
        for i in range(4):
            res = resolutions[i]
            scale = scales[i]
            extRast = os.path.join(r'\\Dataserver1\gpw\GPW4\Release_411\ancillary\extents','gpwv411_extent_'+res+'.tif')
            env.snapRaster = extRast
            env.extent = arcpy.Describe(extRast).extent
    
            outR = os.path.join(outFolder,r.replace("30_sec",res))
            if not arcpy.Exists(outR):
                outAggreg = Aggregate(rPath, scale, "SUM")
                arcpy.CopyRaster_management(outAggreg,outR)
    
        returnList = "Succeeded " + r
    except:
        returnList = "Failed " + r
    return returnList


def main():
    root = r'F:\gpw\v411\rasters_30sec_fixed_zeros'
    
    outFolder = r'F:\gpw\v411\rasters_lower_resolution'
    env.workspace = outFolder
    outRasters = arcpy.ListRasters()

    env.workspace = root
    rList1 = arcpy.ListRasters("*demographic*cntm*") + arcpy.ListRasters("*areakm*") + arcpy.ListRasters("*population_count*")
    #rList = [os.path.join(root,r) for r in rList1 if not r.replace("30_sec","1_deg") in outRasters]
    rList = [os.path.join(root,r) for r in rList1]
    rList.sort()
    
    print("Ready to process {} rasters".format(len(rList)))

    pool = multiprocessing.Pool(processes=min([len(rList),15]),maxtasksperchild=1)
    results = pool.map(aggregate_rasters, rList)
    for result in results:
        print(result)

    pool.close()
    pool.join()
    print("Script complete")


if __name__ == '__main__':
    main()


