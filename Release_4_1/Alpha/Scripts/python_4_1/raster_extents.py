import arcpy, os

rootFolder = r'F:\gpw\gpw_v10_fixed_extents\rasters'
arcpy.env.workspace = rootFolder

rasterList = arcpy.ListRasters()
rasterList.sort()

for raster in rasterList:
    print raster
    desc = arcpy.Describe(raster)

    print desc.extent.XMin
    print desc.extent.XMax
    print desc.extent.YMin
    print desc.extent.YMax

