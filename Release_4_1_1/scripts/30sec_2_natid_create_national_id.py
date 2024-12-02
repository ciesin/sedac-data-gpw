# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 15:55:41 2018

@author: jmills
"""

import arcpy, os, numpy
arcpy.env.overwriteOutput = True

inFolder = r'D:\gpw\release_4_11\national_identifier'

areaFolder = os.path.join(inFolder,'areakm')
scratch = os.path.join(inFolder,'scratch')

natIDpoly = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\global\national_identifier_edits\national_identifier_polygons.gdb\gpw_v4_national_identifier_grid_30_sec'
isoDict = {}
with arcpy.da.SearchCursor(natIDpoly, ["ISOCODE","GRIDCODE"]) as cursor:
    for row in cursor:
        isoDict[row[0]] = row[1]

arcpy.env.workspace = areaFolder
areaTifs = arcpy.ListRasters()
areaTifs.sort()

natID = numpy.zeros((21600, 43200), dtype = int)
areas = numpy.zeros((21600, 43200))

cellsize = 1/120

for a in areaTifs:
    iso = a[:3]
    isoNum = int(isoDict[iso])
    print(iso)
    
    top = float(arcpy.GetRasterProperties_management(a,"TOP").getOutput(0))
    left = float(arcpy.GetRasterProperties_management(a,"LEFT").getOutput(0))
    rows = float(arcpy.GetRasterProperties_management(a,"ROWCOUNT").getOutput(0))
    cols = float(arcpy.GetRasterProperties_management(a,"COLUMNCOUNT").getOutput(0))
    
    topIndex = int(round((90-top)*120,0))
    bottomIndex = int(topIndex + rows)
    leftIndex = int(round(abs(-180-left)*120,0))
    rightIndex = int(leftIndex + cols)
    
    aArr = arcpy.RasterToNumPyArray(a, nodata_to_value=0)
    
    smallArea = areas[topIndex:bottomIndex, leftIndex:rightIndex]
    smallNatID = natID[topIndex:bottomIndex, leftIndex:rightIndex]
    
    smallNatID[aArr>smallArea] = isoNum
    natID[topIndex:bottomIndex, leftIndex:rightIndex] = smallNatID
    
    smallArea[aArr>smallArea] = aArr[aArr>smallArea]
    areas[topIndex:bottomIndex, leftIndex:rightIndex] = smallArea
    
    #fullArea = numpy.zeros((43200, 21600))
    #fullArea[topIndex:bottomIndex, leftIndex:rightIndex] = aArr
    #natID[fullArea>areas] = isoNum
    #areas[fullArea>areas] = fullArea[fullArea>areas]


newRast = arcpy.NumPyArrayToRaster(natID, arcpy.Point(-180.0, -90.0), cellsize, cellsize, 0)
outRast = os.path.join(inFolder,"gpw411_national_identifier.tif")
newRast.save(outRast)

sr = arcpy.Describe(a).SpatialReference
arcpy.DefineProjection_management(outRast,sr)
arcpy.BuildPyramidsandStatistics_management(outRast)
