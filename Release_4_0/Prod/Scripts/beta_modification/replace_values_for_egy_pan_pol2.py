import arcpy, os, datetime
arcpy.CheckOutExtension('Spatial')
    
##Con("replacement_ids_combined" < 2,Con(((
##    "gpw-v4-land-water-area_land.tif" - "replacement_pixels_egy_pan_pol_old_data")
##                                        + "replacement_pixels_egy_pan_pol") < 0,0,
##                                       (("gpw-v4-land-water-area_land.tif" -
##                                         "replacement_pixels_egy_pan_pol_old_data") +
##                                        "replacement_pixels_egy_pan_pol")), "gpw-v4-land-water-area_land.tif")
def main():
    scriptTime = datetime.datetime.now()
    masterList = []
    
    arcpy.env.workspace = r'D:\gpw\4_0_prod\mosaics.gdb'
    repIds = r'D:\gpw\4_0_prod\post_process.gdb\replacement_ids_combined'
    rasters = arcpy.ListRasters("prod_*une*")
    for prodRaster in rasters:
        betaRaster = prodRaster.replace("prod","beta")
        variable = prodRaster[5:]
        if variable == "AREAKMMASKED":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-land-water-area\gpw-v4-land-water-area_land.tif'
        elif variable == "WATERAREAKM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-land-water-area\gpw-v4-land-water-area_water.tif'
        elif variable == "E_ATOTPOPBT_2000_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count\gpw-v4-population-count_2000.tif'
        elif variable == "E_ATOTPOPBT_2005_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count\gpw-v4-population-count_2005.tif'
        elif variable == "E_ATOTPOPBT_2010_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count\gpw-v4-population-count_2010.tif'
        elif variable == "E_ATOTPOPBT_2015_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count\gpw-v4-population-count_2015.tif'
        elif variable == "E_ATOTPOPBT_2020_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count\gpw-v4-population-count_2020.tif'
        elif variable == "UNE_ATOTPOPBT_2000_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals_2000.tif'
        elif variable == "UNE_ATOTPOPBT_2005_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals_2005.tif'
        elif variable == "UNE_ATOTPOPBT_2010_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals_2010.tif'
        elif variable == "UNE_ATOTPOPBT_2015_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals_2015.tif'
        elif variable == "UNE_ATOTPOPBT_2020_CNTM":
            modRaster = r'D:\gpw\4_0_prod\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals_2020.tif'
        try:
            arcpy.env.cellSize = modRaster
            arcpy.env.extent = modRaster
            arcpy.env.mask = repIds
            conRaster = arcpy.sa.Con(arcpy.sa.Raster(repIds)<2,arcpy.sa.Con(
                ((arcpy.sa.Raster(modRaster)-arcpy.sa.Raster(betaRaster))+arcpy.sa.Raster(prodRaster))<0,0,
                ((arcpy.sa.Raster(modRaster)-arcpy.sa.Raster(betaRaster))+arcpy.sa.Raster(prodRaster))),
                arcpy.sa.Raster(modRaster))
            outRaster = r'D:\gpw\4_0_prod\outTifs' + os.sep + os.path.basename(modRaster)
            conRaster.save(outRaster)
            print "Created " + outRaster
        except:
            print arcpy.GetMessages()
                        
   


    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)
    
if __name__ == '__main__':
    main()
