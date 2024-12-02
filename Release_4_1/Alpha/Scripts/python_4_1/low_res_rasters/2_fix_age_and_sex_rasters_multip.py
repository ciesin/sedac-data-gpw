#Jane Mills
#GPW
#fix age grids

import arcpy, os, re, multiprocessing, datetime
from arcpy import env
arcpy.CheckOutExtension("Spatial")
scriptTime = datetime.datetime.now()

def fix_ages(rPath):
    r = os.path.basename(rPath)
    env.overwriteOutput = True
    processTime = datetime.datetime.now()
    outFolder = r'D:\gpw\release_4_1\low_res'
    outR = os.path.join(outFolder,r)

    returnList = []
    res = r[30:-4]

    totPop = os.path.join(outFolder,'gpw_v4_e_atotpopbt_2010_cntm_'+res+'.tif')

    arcpy.gp.Con_sa(totPop,rPath,outR,"","VALUE >= 0")

    returnList.append("Calculated " + r[:-4])
    return returnList

def fix_sexes(rPath):
    r = os.path.basename(rPath)
    env.overwriteOutput = True
    processTime = datetime.datetime.now()
    outFolder = r'D:\gpw\release_4_1\low_res'
    outR = os.path.join(outFolder,r)

    returnList = []
    res = r[29:-4]

    totPop = os.path.join(outFolder,'gpw_v4_e_atotpopbt_2010_cntm_'+res+'.tif')

    arcpy.gp.Con_sa(totPop,rPath,outR,"","VALUE >= 0")

    returnList.append("Calculated " + r[:-4])
    return returnList

def main():
    rootAge = r'D:\gpw\release_4_1\low_res\fix_age'
    rootSex = r'D:\gpw\release_4_1\low_res\fix_sex'

    print "processing"

    env.workspace = rootAge
    ageList = [os.path.join(rootAge,raster) for raster in arcpy.ListRasters()]

    env.workspace = rootSex
    sexList = [os.path.join(rootSex,raster) for raster in arcpy.ListRasters()]

    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
    results = pool.map(fix_ages, ageList)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()

    pool2 = multiprocessing.Pool(processes=5,maxtasksperchild=1)
    results = pool2.map(fix_sexes, sexList)
    for result in results:
        for result2 in result:
            print result2

    pool2.close()
    pool2.join()
    
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)


if __name__ == '__main__':
    main()
