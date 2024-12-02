import arcpy, os, zipfile

rasterIn = r'Z:\GPW4\Release_4_1\Alpha\Gridding\deliverable_tifs'
zipWS = rasterIn
arcpy.env.workspace = rasterIn
rasters = arcpy.ListRasters("*e_*bt*cntm*")
rasters.sort()
for raster in rasters:
    bt = os.path.join(rasterIn,raster)
    mt = bt.replace('bt','mt')
    ft = bt.replace('bt','ft')
    btdens = os.path.join(rasterIn,raster).replace('cntm','dens')
    mtdens = btdens.replace('bt','mt')
    ftdens = btdens.replace('bt','ft')
    zipList = [bt,mt,ft,btdens,mtdens,ftdens]
    if len(raster.split("_")[3])==4:
        outZip = zipWS + os.sep + "gpw_v4_ages_" + raster.split("_")[3] + raster.split("_")[4][:-2]+ "_" + raster.split("_")[-2]+raster.split("_")[-1][:-4]+".zip"
    else:
        outZip = zipWS + os.sep + "gpw_v4_ages_" + raster.split("_")[3][1:4] + "_" + raster.split("_")[3][4:-2]+"_resolution_"+raster.split("_")[-2]+"_"+raster.split("_")[-1][:-4]+".zip"
    zf = zipfile.ZipFile(outZip,mode='w')
    for z in zipList:
##        print z
        zf.write(z,os.path.basename(z),compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
    print outZip
##    break
