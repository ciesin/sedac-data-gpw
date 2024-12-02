#Jane Mills
#7/12/16
#GPW
#Convert to ascii
#Don't use numpy - it changes the values of the rasters

import arcpy, os, multiprocessing, shutil
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

def convert(rPath):
    message = None
    r = os.path.basename(rPath)
    outFolder = r'F:\gpw\v411\ascii'
    arcpy.env.scratchWorkspace = r'F:\gpw\v411\scratch'
    prjFile = r'F:\gpw\v411\ancillary\ascii_prj_file.prj'
    arcpy.env.outputCoordinateSystem = prjFile

    rectangles = ["-180 0 -90 90","-90 0 0 90","0 0 90 90","90 0 180 90",
                  "-180 -90 -90 -0.000001","-90 -90 0 -0.000001","0 -90 90 -0.000001","90 -90 180 -0.000001"]

    try:
        if '30_sec' in r:
            for i in range(len(rectangles)):
                outAscii = os.path.join(outFolder,r[:-4]+'_'+str(i+1)+'.asc')
                if not os.path.exists(outAscii):
                    rect = rectangles[i]
                    outTemp = 'in_memory' + os.sep + r[:-4] + "_" + str(i+1)
                    arcpy.Clip_management(rPath, rect, outTemp)
                    arcpy.RasterToASCII_conversion(outTemp,outAscii)
                
                outPrj = os.path.join(outFolder,r[:-4]+'_'+str(i+1)+'.prj')
                if not os.path.exists(outPrj):
                    shutil.copy(prjFile, outPrj)
                
        else:
            outAscii = os.path.join(outFolder,r[:-4]+'.asc')
            if not os.path.exists(outAscii):
                arcpy.RasterToASCII_conversion(rPath,outAscii)

        message = "Succeeded: " + r
    except:
        message = "Failed: " + r

    return message

def main():
    root = r'F:\gpw\v411\rasters_translate'
    outFolder = r'F:\gpw\v411\ascii'
    
    asciiList = os.listdir(outFolder)
    arcpy.env.workspace = root
    rasterList = arcpy.ListRasters()
    rList = [os.path.join(root,r) for r in rasterList if not r.replace(".tif",".asc") in asciiList]
    rList.sort()

    print("Processing {} rasters".format(len(rList)))
    
    pool = multiprocessing.Pool(processes=min([len(rList),10]),maxtasksperchild=1)
    results = pool.map(convert, rList)
    for result in results:
        print(result)

    pool.close()
    pool.join()
    
    xmlList = [os.path.join(outFolder,f) for f in os.listdir(outFolder) if f[-4:] == ".xml"]
    for xml in xmlList:
        os.remove(xml)
        
    print("Script Complete")


if __name__ == '__main__':
    main()

