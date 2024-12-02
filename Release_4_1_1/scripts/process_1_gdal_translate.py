#Jane Mills
#10/24/2018
#GPW -
import os, multiprocessing, arcpy, shutil

def process(rPath):
    r = os.path.basename(rPath)
    outFolder = r'F:\gpw\v411\rasters_translate'
    outR = os.path.join(outFolder,r)
    message = None
    try:
        if "context" in r or "watermask" in r or "identifier" in r:
            os.system("gdal_translate -ot Int16 -co COMPRESS=LZW -of GTiff " + rPath + " " +  outR)
            inFile = os.path.join(os.path.dirname(rPath),r[:-4] + ".vat.dbf")
            outFile = os.path.join(outFolder,r[:-4] + ".vat.dbf")
            shutil.copy(inFile,outFile)
        else:
            os.system("gdal_translate -ot Float32 -co COMPRESS=LZW -of GTiff " + rPath + " " +  outR)

        message = "Succeeded: " + r
    except:
        message = "Failed: " + r
    return message


def main():
    outFolder = r'F:\gpw\v411\rasters_translate'
    arcpy.env.workspace = outFolder
    outRasters = arcpy.ListRasters()
    
    root1 = r'F:\gpw\v411\rasters_30sec_fixed_zeros'
    root2 = r'F:\gpw\v411\rasters_lower_resolution'
    
    arcpy.env.workspace = root1
    rList1 = [os.path.join(root1,r) for r in arcpy.ListRasters() if r not in outRasters]
    arcpy.env.workspace = root2
    rList2 = [os.path.join(root2,r) for r in arcpy.ListRasters() if r not in outRasters]
    
    rList = rList1 + rList2
    
    print("Processing {} rasters".format(len(rList)))

    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(process, rList)
    for result in results:
        print(result)
    pool.close()
    pool.join()
    print("Translation complete")

    arcpy.BuildPyramidsandStatistics_management(outFolder)
    
    xmlList = [os.path.join(outFolder,f) for f in os.listdir(outFolder) if f[-4:] == ".xml"]
    for xml in xmlList:
        os.remove(xml)
        
    print("Script complete")
 
if __name__ == '__main__':
    main()

