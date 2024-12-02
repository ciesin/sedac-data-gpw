import arcpy, os, zipfile, multiprocessing

rasterIn = r'F:\gpw\ascii'
zipWS = rasterIn+"_zip"
arcpy.env.workspace = rasterIn
rasters = arcpy.ListRasters("*e_*totpopbt*sec_1*")
rasters.sort()
tileList=["_1.","_2.","_3.","_4.","_5.","_6.","_7.","_8."]
for r in rasters:
    for tile in tileList:
        if tile == tileList[0]:
            raster = r
        else:
            raster = r.replace("_1.",tile)
        bt = os.path.join(rasterIn,raster)
##    mt = bt.replace('bt','mt')
##    if not arcpy.Exists(mt):
##        continue
##    ft = bt.replace('bt','ft')
##    btdens = os.path.join(rasterIn,raster).replace('cntm','dens')
##    mtdens = btdens.replace('bt','mt')
##    ftdens = btdens.replace('bt','ft')
        if tile == tileList[0]:
            zipList = [bt]
        else:
            zipList = zipList + [bt]
    prjList = []
    for z in zipList:
        prjList.append(z.replace(".asc",".prj"))
    zipList = zipList + prjList
    print zipList
    
    outZip = zipWS + os.sep + raster.replace("_8.",".") +".zip"
##    zf = zipfile.ZipFile(outZip,mode='w')
##    for z in zipList:
####        print z
##        zf.write(z,os.path.basename(z),compress_type=zipfile.ZIP_DEFLATED)
##    zf.close()
    print outZip
##    break
