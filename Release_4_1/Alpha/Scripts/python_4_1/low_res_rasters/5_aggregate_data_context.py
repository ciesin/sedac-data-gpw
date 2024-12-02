#Jane Mills
#GPW
#Aggregate the national identifier grid

import arcpy, os
from arcpy.sa import *
from arcpy import env
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

rootFolder = r'F:\GPW\aggregate_rasters'
inR = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\high_res\gpw_v4_context.tif'
outF = r'D:\gpw\release_4_1\low_res'
scratch = os.path.join(outF,'scratch')

resolutions = ['2pt5_min','15_min','30_min','1_deg']
scales = ['5','30','60','120']

catDict = {}
with arcpy.da.SearchCursor(inR,["Value","CATEGORY"]) as cursor:
    for row in cursor:
        catDict[row[0]] = row[1]

outR1 = os.path.join(scratch,'context_no_207.tif')
arcpy.gp.Reclassify_sa(inR,"Value","0 0;201 201;202 202;203 203;204 204;205 205;206 206;207 0",outR1, "DATA")

for i in range(4):
    res = resolutions[i]
    print res
    scale = scales[i]
    ext = os.path.join(outF,'extents','gpw4_extent_'+res+'.tif')
    extRast = arcpy.sa.Raster(ext)
    env.snapRaster = ext
    env.extent = extRast.extent

    #aggregate
    outR2 = os.path.join(scratch,'dc_'+res+'_block_stats.tif')
    arcpy.gp.BlockStatistics_sa(outR1,outR2,"Rectangle "+scale+" "+scale+" CELL","MAJORITY","DATA")

    #Set to zero populated areas
    pop = os.path.join(outF,'gpw_v4_e_atotpopbt_2010_cntm_'+res+'.tif')
    outR3 = os.path.join(scratch,'dc_'+res+'_zero_pop.tif')
    arcpy.gp.Con_sa(pop,outR2,outR3, "0", "VALUE = 0")

    #sum up ages
    age1 = os.path.join(outF,'gpw_v4_e_a000_014bt_2010_cntm_'+res+'.tif')
    age2 = os.path.join(outF,'gpw_v4_e_a015_064bt_2010_cntm_'+res+'.tif')
    age3 = os.path.join(outF,'gpw_v4_e_a065plusbt_2010_cntm_'+res+'.tif')
    outR4 = os.path.join(scratch,'sum_ages_'+res+'.tif')
    arcpy.gp.RasterCalculator_sa('"'+age1+'"+"'+age2+'"+"'+age3+'"',outR4)

    #create raster where pop > 0 and age == 0
    outR5 = os.path.join(scratch,'dc_'+res+'_207.tif')
    arcpy.gp.RasterCalculator_sa('Con("'+pop+'",0,1,"Value>0")+Con("'+outR4+'",0,1,"VALUE=0")',outR5)

    #put final two rasters together
    outRName = 'gpw_v4_context_'+res+'.tif'
    outRPath = os.path.join(outF,outRName)
    arcpy.gp.Con_sa(outR5,"207",outRPath,outR3,"VALUE = 0")

    #fix attribute table
    arcpy.AddField_management(outRPath,"CATEGORY","TEXT","","","75")
    with arcpy.da.UpdateCursor(outRPath,["VALUE","CATEGORY"]) as cursor:
        for row in cursor:
            if row[0] in catDict:
                row[1] = catDict[row[0]]
                cursor.updateRow(row)
            else:
                print "found error"



