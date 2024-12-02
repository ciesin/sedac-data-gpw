# rasterize.py
# script to utilize GDAL to create gadm country files

# Import Python Libraries
import arcpy, os
import gdal, ogr
from datetime import datetime

StartTime = datetime.now()
print StartTime

## NOTE THIS CODE WAS RUN ON DEVSEDARC VM PREVIOUSLY
## GDAL MUST BE INSTALLED ON THE MACHINE IT RUNS ON

# Define input workspace
workspace = r"F:\GPW\fishnets\country_boundaries_admin0"  # Update
outWS = r"F:\GPW\fishnets\output_tifs" # Update
# Create driver to produce GeoTiffs
driver = gdal.GetDriverByName( "GTiff" )

# Define input extent
inputExtent = r"F:\GPW\fishnets\gpw4_extent.tif"
# Open Extent File
inputExtentOpen = gdal.Open(inputExtent)
# Set number of raster bands 
nbands = inputExtentOpen.RasterCount
# Set number of columns and rows for -180, -90, 90, 180 --Full Global Extent
ncols = inputExtentOpen.RasterXSize
nrows = inputExtentOpen.RasterYSize
gdal_datatype = gdal.GDT_Byte
# Get input GeoTransform Information
inputExtentGeoTransform = inputExtentOpen.GetGeoTransform()
# Set lower left corner
xllcorner = inputExtentGeoTransform[0]
# Set upper left corner
yulcorner = inputExtentGeoTransform[3]
# Set cell size 
cellsize = inputExtentGeoTransform[1]
# Set projection info
projection = inputExtentOpen.GetProjection()

# Define arcpy workspace
arcpy.env.workspace = workspace
# Create list of shapefiles
shps = arcpy.ListFeatureClasses("*")

# Iterate
for shp in shps:
    print shp
    # Create Search Cursor in order to Get ID_0
    searchRows = arcpy.SearchCursor(shp)
    for row in searchRows:
        id0 = int(row.getValue("ID_0"))
        break
    print id0
    # delete cursor objects to clear locks
    del row
    del searchRows        
   
    # Define input shape string
    inShape = os.path.join(workspace, shp)
    # Open Shapefile
    shapeDataSource = ogr.Open(inShape)
    # Read shp as layer
    shapeLayer = shapeDataSource.GetLayer()

    # Define New Raster File
    shp = shp.upper()
    newFile = outWS + os.path.sep + shp.replace("SHP","tif")
    if os.path.isfile(newFile):
        print "File already exists"
        pass
    else:
        # Create new file
        newRaster = driver.Create(newFile,ncols,nrows,nbands,gdal_datatype)
        # Define geographic extent of new file
        newRaster.SetGeoTransform([xllcorner,cellsize,0,yulcorner,0,-cellsize])
        # Define projection of newRaster
        newRaster.SetProjection(projection)
        # Set noData and Fill values to 255
        newRaster.GetRasterBand(1).SetNoDataValue(255)
        newRaster.GetRasterBand(1).Fill(255)
        # Grab Raster Band
        band = newRaster.GetRasterBand(1)
        # Set NoData Value
        nodata = band.GetNoDataValue()
        band.Fill(nodata)
        # Rasterize shp to raster
        gdal.RasterizeLayer(newRaster,[1],shapeLayer,None,None,[id0],['ALL_TOUCHED=TRUE'])
        print "Created " + newFile

endtime = datetime.now() - StartTime
print endtime
