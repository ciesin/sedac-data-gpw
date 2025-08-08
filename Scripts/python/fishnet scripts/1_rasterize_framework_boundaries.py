# rasterize.py
# script to utilize GDAL to create gadm country files

# Import Python Libraries
import arcpy, os
from osgeo import gdal 
from osgeo import ogr
# Define input workspace
workspace = r"Z:\GPW\GPW5\Preprocessing\Global\framework_boundaries\updated_framework_shp_052925"  # Update
# Define input extents
inputExtents=[r"F:\gpwv5\fishnet\pixel_ids\global_15_second_ids_v2.tif"]#,
              #r"F:\gpwv5\fishnet\pixel_ids\global_30_second_ids.tif"]
for inputExtent in inputExtents:
    if inputExtent == inputExtents[0]:
         outWS = r"F:\gpwv5\fishnet\framework_rasters\15_second"
    else:
         outWS = r"F:\gpwv5\fishnet\framework_rasters\30_second"
    # Create driver to produce GeoTiffs
    driver = gdal.GetDriverByName( "GTiff" )    
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
        print(shp)
        # newFile = outWS + os.path.sep + shp + ".tif"
        newFile = outWS + os.path.sep + shp.replace(".shp",".tif")
        if arcpy.Exists(newFile):
            print(newFile + " already exists")
        else:
            # Create Search Cursor in order to Get ID_0
            searchRows = arcpy.SearchCursor(shp)
            for row in searchRows:
                id0 = int(row.getValue("CIESINCODE"))
                if id0 > 254:
                    id0 = 254
                #id0 = int(row.getValue("STATEFP20"))
                break
            print(id0)
            # delete cursor objects to clear locks
            del row
            del searchRows                
            # Define input shape string
            inShape = os.path.join(workspace, shp)
            # buffer the shape by 2km
            bufferShape=r'F:\gpwv5\fishnet\framework_polygons\buffer_shps'+os.sep+os.path.basename(inShape)
            arcpy.Buffer_analysis(inShape,bufferShape,"2 Kilometers","FULL","ROUND","ALL","#","GEODESIC")
            # Open Shapefile
            shapeDataSource = ogr.Open(bufferShape)
            # Read shp as layer
            shapeLayer = shapeDataSource.GetLayer()
            # Define New Raster File
            shp = shp.upper()        
            # Create new file
            newRaster = driver.Create(newFile,ncols,nrows,nbands,gdal_datatype,options=['COMPRESS=LZW'])
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
            gdal.RasterizeLayer(newRaster,[1],shapeLayer,None,None,[id0],['-at'])
            print("Created " + newFile)