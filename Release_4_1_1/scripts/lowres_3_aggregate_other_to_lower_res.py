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
    scratchF = r'F:\gpw\v411\scratch'
    env.scratchWorkspace = scratchF
    env.compression = "LZW"
    outFolder = r'F:\gpw\v411\rasters_lower_resolution'
    resolutions = ['2pt5_min','15_min','30_min','1_deg']
    scales = ['5','30','60','120']
    returnList = None
    
    try:
        for i in range(4):
            res = resolutions[i]
            scale = scales[i]
            extRast = os.path.join(r'\\Dataserver1\gpw\GPW4\Release_411\ancillary\extents','gpwv411_land_'+res+'.tif')
            env.snapRaster = extRast
            env.extent = arcpy.Describe(extRast).extent
            outR = os.path.join(outFolder,r.replace("30_sec",res))
            
            if "adminunit" in r and not arcpy.Exists(outR):
                outAggreg = Aggregate(rPath, scale, "MEAN")
                arcpy.CopyRaster_management(outAggreg,outR)
                
            if "national" in r and not arcpy.Exists(outR):
                gridDict = {}
                with arcpy.da.SearchCursor(rPath,["VALUE","ISOCODE","UNSDCODE","NAME0","CIESINCODE"]) as cursor:
                    for row in cursor:
                        gridDict[row[0]] = row[1:]
                        
                outBS = BlockStatistics(rPath, NbrRectangle(int(scale),int(scale)), "MAJORITY")
                outAggreg = Aggregate(outBS, scale, "MEDIAN")
                arcpy.CopyRaster_management(outAggreg,outR)
                
                arcpy.AddField_management(outR,"ISOCODE","TEXT","","","5")
                arcpy.AddField_management(outR,"UNSDCODE","SHORT","5")
                arcpy.AddField_management(outR,"NAME0","TEXT","","","100")
                arcpy.AddField_management(outR,"CIESINCODE","SHORT","5")
            
                with arcpy.da.UpdateCursor(outR,["VALUE","ISOCODE","UNSDCODE","NAME0","CIESINCODE"]) as cursor:
                    for row in cursor:
                        if row[0] in gridDict:
                            row[1:] = gridDict[row[0]]
                            cursor.updateRow(row)
            
            if "watermask" in r and not arcpy.Exists(outR):
                n = int(scale)*int(scale)
                outCon1 = Con(Raster(rPath) != 2, Raster(rPath))
                tempR = os.path.join(scratchF, os.path.basename(outR))
                outAggreg = Aggregate(outCon1, scale, "SUM")
                outAggreg.save(tempR)
                outCon = Con(IsNull(Raster(tempR)) == 1, 2, Con(Raster(tempR) == 0, 0, Con(Raster(tempR) == 3*n, 3, 1)))
                arcpy.CopyRaster_management(outCon,outR)
                
                arcpy.AddField_management(outR,"CATEGORY","TEXT","","",50)
                with arcpy.da.UpdateCursor(outR,["VALUE","CATEGORY"]) as cursor:
                    for row in cursor:
                        if row[0] == 0: row[1] = "Total Water Pixels"
                        if row[0] == 1: row[1] = "Partial Water Pixels"
                        if row[0] == 2: row[1] = "Total Land Pixels"
                        if row[0] == 3: row[1] = "Ocean Pixels"
                        cursor.updateRow(row)
            
            if "context" in r and not arcpy.Exists(outR):
                male = os.path.join(outFolder,'gpw_v4_basic_demographic_characteristics_rev11_atotpopmt_2010_cntm_{}.tif'.format(res))
                female = os.path.join(outFolder,'gpw_v4_basic_demographic_characteristics_rev11_atotpopft_2010_cntm_{}.tif'.format(res))
                total = os.path.join(outFolder,'gpw_v4_basic_demographic_characteristics_rev11_atotpopbt_2010_cntm_{}.tif'.format(res))
                
                conZero = Con((Raster(rPath) == 204) | (Raster(rPath) == 205), Raster(rPath))
                bsZero = BlockStatistics(conZero, NbrRectangle(int(scale),int(scale)), "MAJORITY")
                aggZero = Aggregate(bsZero, scale, "MEDIAN")
                tempZero = os.path.join(scratchF, os.path.basename(outR)[:-4]+"_agg_zero.tif")
                aggZero.save(tempZero)
                
                conNoData = Con((Raster(rPath) == 201) | (Raster(rPath) == 202) | (Raster(rPath) == 203) | (Raster(rPath) == 206), Raster(rPath))
                bsND = BlockStatistics(conNoData, NbrRectangle(int(scale),int(scale)), "MAJORITY")
                aggND = Aggregate(bsND, scale, "MEDIAN")
                tempND = os.path.join(scratchF, os.path.basename(outR)[:-4]+"_agg_nd.tif")
                aggND.save(tempND)

                tempDiff = os.path.join(scratchF,os.path.basename(outR)[:-4]+"_207.tif")
                popDiff = Con((Raster(total)!=0) & (IsNull(Raster(male))==1) & (IsNull(Raster(female))==1), 207, 0)
                popDiff.save(tempDiff)
                
                outCon = Con(Raster(total) == 0, Raster(tempZero), Con(IsNull(Raster(total)) == 1, Raster(tempND), Con(Raster(total) > 0, tempDiff)))
                arcpy.CopyRaster_management(outCon,outR)
                
                arcpy.AddField_management(outR,"CATEGORY","TEXT","","","100")
                with arcpy.da.UpdateCursor(outR,["VALUE","CATEGORY"]) as cursor:
                    for row in cursor:
                        if row[0] == 0: row[1] = "Not applicable"
                        if row[0] == 201: row[1] = "Park or protected area"
                        if row[0] == 202: row[1] = "Military district, airport zone, or other infrastructure"
                        if row[0] == 203: row[1] = "Not enumerated or not reported in census"
                        if row[0] == 204: row[1] = "No households"
                        if row[0] == 205: row[1] = "Uninhabited"
                        if row[0] == 206: row[1] = "Population not gridded"
                        if row[0] == 207: row[1] = "Missing age and/or sex data"
                        cursor.updateRow(row)

        returnList = "Succeeded " + r
    except:
        returnList = "Failed " + r
    return returnList


def main():
    root = r'F:\gpw\v411\rasters_30sec_fixed_zeros'
    env.workspace = root
    inRasters = arcpy.ListRasters()
    
    outFolder = r'F:\gpw\v411\rasters_lower_resolution'
    env.workspace = outFolder
    outRasters = arcpy.ListRasters()

    rList = [os.path.join(root,r) for r in inRasters if not r.replace("30_sec","1_deg") in outRasters]
    rList.sort()
    
    print("Set up complete")

    pool = multiprocessing.Pool(processes=min([len(rList),4]),maxtasksperchild=1)
    results = pool.map(aggregate_rasters, rList)
    for result in results:
        print(result)

    pool.close()
    pool.join()
    print("Script complete")


if __name__ == '__main__':
    main()


