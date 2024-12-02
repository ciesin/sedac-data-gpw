# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 14:35:41 2018

@author: jmills
"""

import arcpy, numpy, os
from scipy import ndimage
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

arcpy.env.scratchWorkspace = r'F:\gpw\v411\scratch'
arcpy.env.compression = "LZW"
arcpy.env.overwriteOutput = True

root = r'F:\gpw\v411\ancillary'
natid = r'F:\gpw\v411\rasters_30sec_fixed_zeros\gpw_v4_national_identifier_grid_rev11_30_sec.tif'
water = r'F:\gpw\v411\scratch\gpw_v4_watermask.tif'

extRast = os.path.join(root,'populated_cells.tif')
outCon = Con(Raster(natid) > 0, 1)
arcpy.CopyRaster_management(outCon, extRast)

extArr = arcpy.RasterToNumPyArray(extRast,"","","",-1)
extArr[extArr > 0] = 1
#k = numpy.array([[0,1,0],[1,0,1],[0,1,0]])
k = numpy.array([[1,1,1],[1,0,1],[1,1,1]])

neighbors = ndimage.convolve(extArr, k, mode='constant', cval=0.0)

#neighbors[neighbors < 4] = 2    #coastal
#neighbors[neighbors == 4] = 1   #inland
#neighbors[extArr == -1] = 3    #ocean

neighbors[neighbors < 8] = 1    #coastal
neighbors[neighbors == 8] = 2   #inland
neighbors[extArr == -1] = 3    #ocean

waterArr = arcpy.RasterToNumPyArray(water,"","","",2)
waterArr[waterArr < 0] = 2
neighbors[neighbors == 2] = waterArr[neighbors == 2]


bottom = arcpy.GetRasterProperties_management(extRast,"BOTTOM")
left = arcpy.GetRasterProperties_management(extRast,"LEFT")
cellx = arcpy.GetRasterProperties_management(extRast,"CELLSIZEX")
celly = arcpy.GetRasterProperties_management(extRast,"CELLSIZEY")
arcpy.env.outputCoordinateSystem = arcpy.Describe(extRast).SpatialReference

newRast = arcpy.NumPyArrayToRaster(neighbors, arcpy.Point(float(left.getOutput(0)), float(bottom.getOutput(0))),
                                   float(cellx.getOutput(0)), float(celly.getOutput(0)), -1)

outRast = os.path.join(root,"water_classification.tif")
newRast.save(outRast)

