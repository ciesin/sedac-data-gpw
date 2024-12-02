# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 15:55:41 2018

@author: jmills
"""

import arcpy, os

r30Folder = r'F:\gpw\v411\rasters_30sec_fixed_zeros'
rLowFolder = r'F:\gpw\v411\rasters_lower_resolution'
polyFolder = r'\\dataserver1\gpw\GPW4\Release_411\data\national_identifier_polygons'
rFolder = r'\\dataserver1\gpw\GPW4\Release_411\data\netCDF\quality_tifs'

nid30 = [os.path.join(r30Folder,r) for r in os.listdir(r30Folder) if r[-4:] == ".tif" and "national" in r]
lownid = [os.path.join(rLowFolder,r) for r in os.listdir(rLowFolder) if r[-4:] == ".tif" and "national" in r]

nids = nid30 + lownid

natIDtable = r'\\Dataserver1\gpw\GPW4\Release_411\data\national_identifier_polygons\gpw_v4_national_identifier_grid_rev11_30_sec.shp'
fList = arcpy.ListFields(natIDtable)[4:]
fNames = [f.name for f in fList]

nidDict = {}
with arcpy.da.SearchCursor(natIDtable, ["Value"]+fNames) as cursor:
    for row in cursor:
        nidDict[row[0]] = row[1:]

for nid in nids[1:]:
    print(nid)
    res = "_".join(os.path.basename(nid)[:-4].split("_")[-2:])
    fieldNames = [f.name for f in arcpy.ListFields(nid)]
    for f in fList:
        if f.name not in fieldNames:
            if f.type == "String":
                arcpy.AddField_management(nid,f.name,f.type,"","",f.length)
            else:
                arcpy.AddField_management(nid,f.name,f.type)
    
    with arcpy.da.UpdateCursor(nid,["Value"]+fNames) as cursor:
        for row in cursor:
            if row[0] in nidDict:
                row[1:] = nidDict[row[0]]
                cursor.updateRow(row)
            else:
                print("Found row not in dict: {}".format(row[0]))

    #Convert to polygon
    outFC1 = os.path.join(polyFolder, os.path.basename(nid)[:-4]+"_single.shp")
    outFC = os.path.join(polyFolder, os.path.basename(nid)[:-4]+".shp")
    arcpy.RasterToPolygon_conversion(nid,outFC1,"NO_SIMPLIFY","Value")
    arcpy.AddField_management(outFC1,"Value","LONG")
    arcpy.CalculateField_management(outFC1,"Value","!gridcode!","PYTHON")
    
    arcpy.Dissolve_management(outFC1,outFC,"Value")
    arcpy.Delete_management(outFC1)
    
    for f in fList:
        if f.type == "String":
            arcpy.AddField_management(outFC,f.name,f.type,"","",f.length)
        else:
            arcpy.AddField_management(outFC,f.name,f.type)
    
    with arcpy.da.UpdateCursor(outFC,["Value"]+fNames) as cursor:
        for row in cursor:
            if row[0] in nidDict:
                row[1:] = nidDict[row[0]]
                cursor.updateRow(row)
            else:
                print("Found row not in dict: {}".format(row[0]))
                
    #Convert back to raster    
    extRast = os.path.join(r'\\Dataserver1\gpw\GPW4\Release_411\ancillary\extents','gpwv411_extent_'+res+'.tif')
    arcpy.env.snapRaster = extRast
    arcpy.env.extent = arcpy.Describe(extRast).extent
    cellsize = arcpy.GetRasterProperties_management(extRast,"CELLSIZEX")
    arcpy.env.compression = "LZW"
    
    for f in fList:
        if f.type == "Integer":
            outR = os.path.join(rFolder,"gpw_v4_national_identifier_grid_rev11_"+f.name.lower()+"_"+res+".tif")
            arcpy.PolygonToRaster_conversion(outFC,f.name,outR,"","",cellsize)
    
xmlList = [os.path.join(polyFolder,f) for f in os.listdir(polyFolder) if f[-4:] == ".xml"]
for xml in xmlList:
    os.remove(xml)
    
xmlList = [os.path.join(rFolder,f) for f in os.listdir(rFolder) if f[-4:] != ".tif"]
for xml in xmlList:
    os.remove(xml)
    
    