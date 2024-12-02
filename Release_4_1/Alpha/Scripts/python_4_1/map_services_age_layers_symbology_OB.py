import arcpy, os, csv
from arcpy import env

rootFolder = r"F:\arcgisserver\serverdata\gpw\gpw-v4-basic-demographic-characteristics-rev10\map-services"
arcpy.env.workspace = rootFolder
arcpy.env.overwriteOutput = True

mxd = arcpy.mapping.MapDocument(os.path.join(rootFolder,"gpw_v4_basic_demographic_characteristics_rev10_script.mxd"))

csvFile = r"\\dataserver0\GPW\GPW4\Release_4_1\Alpha\Cartographic\tables\raster_age_group_names.csv"
openCSV = csv.reader(open(csvFile, "r"))
next(openCSV,None)

for row in openCSV:
    rasterName = row[0]
    print rasterName
    layerName = row[1]
    description = row[2]

    # List layers in mxd
    layers = arcpy.mapping.ListLayers(mxd,rasterName)

    for lyr in layers:
        lyr.name = layerName
        lyr.description = description

        #arcpy.RefreshTOC()

mxd.save()
print "complete"
