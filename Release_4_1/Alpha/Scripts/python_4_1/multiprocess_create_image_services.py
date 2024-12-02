# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process((wildcard,addList)):
    processTime = datetime.datetime.now()
    arcpy.CheckOutExtension("SPATIAL")
    returnList = []
    try:
        mosFolder = r'D:\gpw\release_4_1\image_services'
        variable = wildcard[:-4]
        iso = 'gpw_v4' + variable.lower()
        mosGDB = mosFolder + os.sep + iso + ".gdb"
        mosDS = mosGDB + os.sep + iso
        arcpy.env.compression = "LZW"
        if not arcpy.Exists(mosGDB):
            arcpy.CreateFileGDB_management(mosFolder,iso)
            try:
                if wildcard == '_PIXELAREA.tif':
                    operator="FIRST"
                    bitDepth="32_BIT_FLOAT"
                elif wildcard == '_MEAN_MASKEDADMINAREA.tif':
                    operator="MEAN"
                    bitDepth="32_BIT_FLOAT"
                elif wildcard == '_CONTEXT.tif':
                    operator="FIRST"
                    bitDepth="8_BIT_UNSIGNED"
                elif wildcard == '_NUMINPUTS.tif':
                    operator="SUM"
                    bitDepth="8_BIT_UNSIGNED"
                else:
                    operator="SUM"
                    bitDepth="32_BIT_FLOAT"
                arcpy.CreateMosaicDataset_management(mosGDB,iso,arcpy.SpatialReference(4326),1,bitDepth)
                arcpy.AddRastersToMosaicDataset_management(mosDS,"Raster Dataset", addList,"UPDATE_CELL_SIZES","UPDATE_BOUNDARY")
                arcpy.CalculateStatistics_management(mosDS)
                arcpy.SetMosaicDatasetProperties_management(mosDS,mosaic_operator=operator,default_compression_type='LZ77')
                arcpy.BuildOverviews_management(mosDS)
            except:
                returnList.append("Error creating mosaic dataset: " + iso)
                return returnList
        try:
            landArea = r'D:\gpw\release_4_1\merge\gpw_v4_maskedareakm.tif'
            waterMask = r'D:\gpw\release_4_1\ancillary\gpw_v4_total_water_pixels_isnull.tif'
            tifWS = r'D:\gpw\release_4_1\merge'#mosGDB#
            outRaster = tifWS + os.sep + iso+ ".tif"
            arcpy.env.compression = "LZW"
##            arcpy.CopyRaster_management(mosDS,outRaster)
            densRaster = tifWS + os.sep + iso[:-5] + "_dens.tif"
            snRaster = arcpy.sa.SetNull(arcpy.Raster(waterMask)==0,arcpy.Raster(mosDS))
            arcpy.CopyRaster_management(snRaster,outRaster)
##            snRaster.save(outRaster)
##            outReclass = r'D:\gpw\release_4_1\final\pop0reclass.tif'
##            finalRaster = arcpy.sa.Con(arcpy.Raster(outReclass)==1,0,snRaster)
##            finalRaster.save(outRaster)
            densOut = arcpy.sa.Divide(snRaster,arcpy.Raster(landArea))
##            densOut.save(densRaster)
            arcpy.CopyRaster_management(densOut,densRaster)
            arcpy.BuildPyramidsandStatistics_management(outRaster)
            arcpy.BuildPyramidsandStatistics_management(densRaster)
##            arcpy.RasterToOtherFormat_conversion(mosDS,tifWS,'TIFF')
        except:
            returnList.append("Error Creating tif: " + outRaster + " " + str(arcpy.GetMessages()))
            return returnList
        returnList.append("Processed "+ iso + " " + str(datetime.datetime.now()-processTime))
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
    return returnList

def main():
    workspace = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    # each image service must add rasters from country_tifs and boundary_context_tifs
    countryTifsFolder = r'D:\gpw\release_4_1\country_tifs'
    bcTifsFolder = r'D:\gpw\release_4_1\boundary_context_tifs'
    # generate a list of countryTifFolders
    arcpy.env.workspace = countryTifsFolder
    countryList = arcpy.ListWorkspaces("*","FOLDER")
##    bcList = [os.path.join(bcTifsFolder,os.path.basename(iso)) for iso in countryList if arcpy.Exists(os.path.join(bcTifsFolder,os.path.basename(iso)))]
    procList = []
##    wildcards = ['_MASKEDAREAKM.tif','_MEAN_MASKEDADMINAREA.tif','_WATERAREAKM.tif','_AREAKM.tif','_PIXELAREA.tif','_CONTEXT.tif','_NUMINPUTS.tif','_E_ATOTPOPBT_2010_CNTM.tif']
##    wildcards =['_E_A000_004BT_2010_CNTM.tif','_E_A000_004FT_2010_CNTM.tif','_E_A000_004MT_2010_CNTM.tif',
##                '_E_A000_014BT_2010_CNTM.tif','_E_A005_009BT_2010_CNTM.tif','_E_A005_009FT_2010_CNTM.tif',
##                '_E_A005_009MT_2010_CNTM.tif','_E_A010_014BT_2010_CNTM.tif','_E_A010_014FT_2010_CNTM.tif',
##                '_E_A010_014MT_2010_CNTM.tif','_E_A015_019BT_2010_CNTM.tif','_E_A015_019FT_2010_CNTM.tif',
##                '_E_A015_019MT_2010_CNTM.tif','_E_A015_064BT_2010_CNTM.tif','_E_A020_024BT_2010_CNTM.tif',
##                '_E_A020_024FT_2010_CNTM.tif','_E_A020_024MT_2010_CNTM.tif','_E_A025_029BT_2010_CNTM.tif',
##                '_E_A025_029FT_2010_CNTM.tif','_E_A025_029MT_2010_CNTM.tif','_E_A030_034BT_2010_CNTM.tif',
##                '_E_A030_034FT_2010_CNTM.tif','_E_A030_034MT_2010_CNTM.tif','_E_A035_039BT_2010_CNTM.tif',
##                '_E_A035_039FT_2010_CNTM.tif','_E_A035_039MT_2010_CNTM.tif','_E_A040_044BT_2010_CNTM.tif',
##                '_E_A040_044FT_2010_CNTM.tif','_E_A040_044MT_2010_CNTM.tif','_E_A045_049BT_2010_CNTM.tif',
##                '_E_A045_049FT_2010_CNTM.tif','_E_A045_049MT_2010_CNTM.tif','_E_A050_054BT_2010_CNTM.tif',
##                '_E_A050_054FT_2010_CNTM.tif','_E_A050_054MT_2010_CNTM.tif','_E_A055_059BT_2010_CNTM.tif',
##                '_E_A055_059FT_2010_CNTM.tif','_E_A055_059MT_2010_CNTM.tif','_E_A060_064BT_2010_CNTM.tif',
##                '_E_A060_064FT_2010_CNTM.tif','_E_A060_064MT_2010_CNTM.tif','_E_A065PLUSFT_2010_CNTM.tif',
##                '_E_A065PLUSBT_2010_CNTM.tif','_E_A065PLUSMT_2010_CNTM.tif','_E_A065_069BT_2010_CNTM.tif',
##                '_E_A065_069FT_2010_CNTM.tif','_E_A065_069MT_2010_CNTM.tif','_E_A070PLUSBT_2010_CNTM.tif',
##                '_E_A070PLUSFT_2010_CNTM.tif','_E_A070PLUSMT_2010_CNTM.tif','_E_A070_074BT_2010_CNTM.tif',
##                '_E_A070_074FT_2010_CNTM.tif','_E_A070_074MT_2010_CNTM.tif','_E_A075PLUSBT_2010_CNTM.tif',
##                '_E_A075PLUSFT_2010_CNTM.tif','_E_A075PLUSMT_2010_CNTM.tif','_E_A075_079BT_2010_CNTM.tif',
##                '_E_A075_079FT_2010_CNTM.tif','_E_A075_079MT_2010_CNTM.tif','_E_A080PLUSBT_2010_CNTM.tif',
##                '_E_A080PLUSFT_2010_CNTM.tif','_E_A080PLUSMT_2010_CNTM.tif','_E_A080_084BT_2010_CNTM.tif',
##                '_E_A080_084FT_2010_CNTM.tif','_E_A080_084MT_2010_CNTM.tif','_E_A085PLUSBT_2010_CNTM.tif',
##                '_E_A085PLUSFT_2010_CNTM.tif','_E_A085PLUSMT_2010_CNTM.tif','_E_ATOTPOPBT_1975_CNTM.tif',
##                '_E_ATOTPOPBT_1990_CNTM.tif','_E_ATOTPOPBT_2000_CNTM.tif','_E_ATOTPOPBT_2005_CNTM.tif',
##                '_E_ATOTPOPBT_2015_CNTM.tif','_E_ATOTPOPBT_2020_CNTM.tif',
##                '_UNE_ATOTPOPBT_1975_CNTM.tif','_E_ATOTPOPFT_2010_CNTM.tif','_E_ATOTPOPMT_2010_CNTM.tif',
##                '_UNE_ATOTPOPBT_1990_CNTM.tif','_UNE_ATOTPOPBT_2000_CNTM.tif','_UNE_ATOTPOPBT_2005_CNTM.tif',
##                '_UNE_ATOTPOPBT_2010_CNTM.tif','_UNE_ATOTPOPBT_2015_CNTM.tif','_UNE_ATOTPOPBT_2020_CNTM.tif',
##                '_E_A015_049FT_2010_CNTM.tif']
    wildcards =['_E_A050_054FT_2010_CNTM.tif','_E_A060_064BT_2010_CNTM.tif']

    for wildcard in wildcards:
        addList = []
        for country in countryList:
            arcpy.env.workspace = country
            subFolders = arcpy.ListWorkspaces("*","FOLDER")
            if len(subFolders)==0:
                raster = country + os.sep + os.path.basename(country).upper() + wildcard 
                if not arcpy.Exists(raster):
                    print country + " is missing a raster for " + wildcard
                else:
                    addList.append(raster)
            else:
                for subFolder in subFolders:
                    arcpy.env.workspace = subFolder
                    raster = subFolder + os.sep + os.path.basename(subFolder).upper() + wildcard 
                    if not arcpy.Exists(raster):
                        print subFolder + " is missing a raster for " + wildcard
                    else:
                        addList.append(raster)
        procList.append((wildcard,addList))
                        
    pool = multiprocessing.Pool(processes=2,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
