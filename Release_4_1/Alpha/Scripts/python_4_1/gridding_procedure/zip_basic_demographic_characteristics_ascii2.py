import arcpy, os, zipfile

rasterIn = r'F:\gpw\ascii'
zipWS = rasterIn+"_zip"
arcpy.env.workspace = rasterIn
rasters = arcpy.ListRasters("*_e_*totpopbt*2010*cntm*sec_1*")
rasters.sort()
tileList=["_1.","_2.","_3.","_4.","_5.","_6.","_7.","_8."]
for r in rasters:
    for tile in tileList:
        if tile == tileList[0]:
            raster = r
        else:
            raster = r.replace("_1.",tile)
        bt = os.path.join(rasterIn,raster)
        mt = bt.replace('bt','mt')
        if not arcpy.Exists(mt):
            continue
        ft = bt.replace('bt','ft')
        btdens = os.path.join(rasterIn,raster).replace('cntm','dens')
        mtdens = btdens.replace('bt','mt')
        ftdens = btdens.replace('bt','ft')
        if tile == tileList[0]:
            zipList = [bt,mt,ft,btdens,mtdens,ftdens]
        else:
            zipList = zipList + [bt,mt,ft,btdens,mtdens,ftdens]
    prjList = []
    for z in zipList:
        prjList.append(z.replace(".asc",".prj"))
    zipList = zipList + prjList
##    print zipList
    if len(raster.split("_")[3])==4:
        outZip = zipWS + os.sep + "gpw_v4_ages_" + raster.split("_")[3][1:4] + "_"+ raster.split("_")[4][:-2]+ "_resolution_" + raster.split("_")[-3]+"_"+raster.split("_")[-2]+".asc.zip"
    else:
        outZip = zipWS + os.sep + "gpw_v4_ages_" + raster.split("_")[3][1:4] + "_" + raster.split("_")[3][4:-2]+"_resolution_"+raster.split("_")[-3]+"_"+raster.split("_")[-2]+".asc.zip"
    zf = zipfile.ZipFile(outZip,mode='w')
    for z in zipList:
##        print z
        zf.write(z,os.path.basename(z),compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
    print outZip
##    break
