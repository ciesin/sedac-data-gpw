import arcpy, os, zipfile, multiprocessing

rasterIn = r'F:\gpw\ascii'
zipWS = rasterIn+"_zip"
arcpy.env.workspace = rasterIn
##rasters = arcpy.ListRasters("*national_identifier*min*")+arcpy.ListRasters("*national_identifier*deg*")
rasters = arcpy.ListRasters("*national_identifier*sec*_1*")
rasters.sort()
tileList=["_1.","_2.","_3.","_4.","_5.","_6.","_7.","_8."]
for r in rasters:
##    raster = r
##    bt = os.path.join(rasterIn,raster)
    for tile in tileList:
        if tile == tileList[0]:
            raster = r
        else:
            raster = r.replace("_1.",tile)
        bt = os.path.join(rasterIn,raster)
        if tile == tileList[0]:
            zipList = [bt]
        else:
            zipList = zipList + [bt]
##    zipList = [bt]
    prjList = []
    for z in zipList:
        prjList.append(z.replace(".asc",".prj"))
    zipList = zipList + prjList
    zipList.append(r'F:\gpw\ascii\gpw_v4_national_identifier_lookup.txt')
    zipList.append(r'F:\gpw\gpw-v4-national-identifier-grid_polygons.cpg')
    zipList.append(r'F:\gpw\gpw-v4-national-identifier-grid_polygons.dbf')
    zipList.append(r'F:\gpw\gpw-v4-national-identifier-grid_polygons.prj')
    zipList.append(r'F:\gpw\gpw-v4-national-identifier-grid_polygons.sbn')
    zipList.append(r'F:\gpw\gpw-v4-national-identifier-grid_polygons.sbx')
    zipList.append(r'F:\gpw\gpw-v4-national-identifier-grid_polygons.shp')
    zipList.append(r'F:\gpw\gpw-v4-national-identifier-grid_polygons.shx')
    print zipList
    
    outZip = zipWS + os.sep + raster.replace("_8.",".") +".zip"
    zf = zipfile.ZipFile(outZip,mode='w')
    for z in zipList:
##        print z
        zf.write(z,os.path.basename(z),compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
    print outZip
##    break
