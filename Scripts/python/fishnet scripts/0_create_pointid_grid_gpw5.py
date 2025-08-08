# create_pointid_grid.py
# Author: Kytt MacManus
# Script to create global Pixel ID Grid
# Updated for GPWv5, 7/20/23, Linda Pistolesi
# Ran from Python Command window with Python 3.9.16 rather than from VS Code to avoid issues.

# Import Python Libraries
import arcpy, os
from osgeo import gdal
import numpy as np

# Create driver to produce GeoTiffs
driver = gdal.GetDriverByName( "GTiff" )

# Define Extent File
#inputExtent = r'F:\gpwv5\fishnet\pointid_rasters\3_second\usadc_ids.tif'
inputExtent = r"\\dataserver1\GPW\GPW5\Input_Data\Global_Regional\Fishnets\global_15arcsec_raster\global_const.tif" # PROVIDE PATH TO RASTER IN THE EXTENT AND CELL SIZE DESIRED
#inputExtent = r"F:\gpwv5\fishnet\scratch\casa\GHS_POP_E2025_GLOBE_R2023A_4326_3ss_V1_0-003.tif"

# Define ouput file
newFile = r"F:\gpwv5\fishnet\pixel_ids\global_15_second_ids_v2.tif" ## + os.sep + raster.replace("extent","ids") #######UPDATE
if arcpy.Exists(newFile):
    print (newFile + " already exists")
else:
    print ("Processing " + inputExtent)
    # Open Extent File
    inputExtentOpen = gdal.Open(inputExtent)
    # Set number of raster bands 
    nbands = inputExtentOpen.RasterCount
    # Set number of columns and rows for -180, -90, 90, 180 --Full Global Extent
    ncols = inputExtentOpen.RasterXSize
    nrows = inputExtentOpen.RasterYSize
    # Determine appropriate GDAL Data Type and Assign to Variable
    if ncols * nrows < 256:    
        # Set GDAL data type
        gdal_datatype = gdal.GDT_Byte
    elif ncols * nrows < 65536 and ncols * nrows > 255:
        gdal_datatype = gdal.GDT_UInt16
    elif ncols * nrows <  4294967296 and ncols * nrows > 65535:
        gdal_datatype = gdal.GDT_Int32
    gdal_datatype = gdal.GDT_Int64
    # Get input GeoTransform Information
    inputExtentGeoTransform = inputExtentOpen.GetGeoTransform()
    # Set lower left corner
    xllcorner = inputExtentGeoTransform[0]
    # Set upper left corner
    yulcorner = inputExtentGeoTransform[3]
    # Set cell size 
    cellsize = inputExtentGeoTransform[1]
    # Determine the total number of pixels
    ##print "Reading"
    inputArray = inputExtentOpen.ReadAsArray()
    numPixels = inputArray.size
    ##print inputArray.size
    # Create new file
    newRaster = driver.Create(newFile,ncols,nrows,nbands,gdal_datatype,options=['COMPRESS=LZW','BIGTIFF=YES'])
    print ("Created " + newFile)
    # Define geographic extent of new file
    newRaster.SetGeoTransform([xllcorner,cellsize,0,yulcorner,0,-cellsize])
    ### Read new file as an array
    ##newRasterArray = newRaster.ReadAsArray()
    # Create sequential integer array for total number of pixels globally
    idMap = np.arange(-46185765821,46185765822)
    print ("Created sequential integer array")
    # Reshape sequential integer array to full global extent in 2 dimensions
    newMap = idMap.reshape((nrows, ncols))
    # Write sequential integer values to raster file
    newRaster.GetRasterBand(1).WriteArray(newMap)
    # Clear locks
    newRaster = None
    # Use Arcpy to define projection
    try:
        WGS84 = arcpy.SpatialReference(4326)
        arcpy.DefineProjection_management(newFile, WGS84)
        arcpy.BuildPyramids_management(newFile)
        print ("Defined Projection")
    except:
        print (arcpy.GetMessages())


