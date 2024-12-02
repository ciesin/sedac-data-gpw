import arcpy, os, zipfile

rasterIn = r'F:\gpw\ascii'
zipWS = rasterIn+"_zip"
arcpy.env.workspace = rasterIn
rasters = arcpy.ListRasters("*e_*totpopbt*min*")+arcpy.ListRasters("*e_*totpopbt*deg*")
rasters.sort()
for raster in rasters:
    bt = os.path.join(rasterIn,raster)
##    mt = bt.replace('bt','mt')
##    if not arcpy.Exists(mt):
##        continue
##    ft = bt.replace('bt','ft')
##    btdens = os.path.join(rasterIn,raster).replace('cntm','dens')
##    mtdens = btdens.replace('bt','mt')
##    ftdens = btdens.replace('bt','ft')
    zipList = [bt]#,mt,ft,btdens,mtdens,ftdens]
    prjList = []
    for z in zipList:
        prjList.append(z.replace(".asc",".prj"))
    zipList = zipList + prjList
##    print zipList
    
    outZip = zipWS + os.sep + raster +".zip"
    zf = zipfile.ZipFile(outZip,mode='w')
    for z in zipList:
##        print z
        zf.write(z,os.path.basename(z),compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
    print outZip
##    break
