#Jane Mills
#7/12/16
#GPW
#Validate the grids

import arcpy, os, re, multiprocessing, datetime
from arcpy import env
arcpy.CheckOutExtension("Spatial")
scriptTime = datetime.datetime.now()
arcpy.env.overwriteOutput = True

def convert(r):
    returnList = []
    rName = os.path.basename(r)
    outFolder = r'F:\gpw\gpw4_rev10_fixed_extents\ascii'
    scratch = r'F:\gpw\gpw4_rev10_fixed_extents\scratch'

    #X-Minimum, Y-Minimum, X-Maximum, Y-Maximum
    rectangles = ["-180 0 -90 90","-90 0 0 90","0 0 90 90","90 0 180 90",
                  "-180 -90 -90 -0.000001","-90 -90 0 -0.000001","0 -90 90 -0.000001","90 -90 180 -0.000001"]

    if '30_sec' in rName:
        for i in range(len(rectangles)):
            outAscii = os.path.join(outFolder,rName[:-4]+'_'+str(i+1)+'.asc')
            rect = rectangles[i]
            outTemp = os.path.join(scratch,rName[:-4]+'_'+str(i+1)+'.tif')
            arcpy.Clip_management(r, rect, outTemp)
            arcpy.RasterToASCII_conversion(outTemp,outAscii)
            arcpy.Delete_management(outTemp)
        returnList.append("Calculated " + rName[:-4])

    else:
        outAscii = os.path.join(outFolder,rName[:-4]+'.asc')
        if os.path.exists(outAscii):
            returnList.append("Already done: " + rName[:-4])
            pass
        else:
            arcpy.RasterToASCII_conversion(r,outAscii)
            returnList.append("Calculated " + rName[:-4])

    return returnList

def main():
    root = r'F:\gpw\gpw4_rev10_fixed_extents\rasters'
    print "processing"

    env.workspace = root
    rList = [os.path.join(root,r) for r in arcpy.ListRasters("*_une_*")]
    rList.sort()

    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(convert, rList)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)


if __name__ == '__main__':
    main()
