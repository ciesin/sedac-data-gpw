import arcpy, os
from arcpy import env
from arcpy.sa import *


arcpy.CheckOutExtension("Spatial")
arcpy.env.workspace = r"\\F:\arcgisserver\serverdata\usgrids\sf1_2010"
arcpy.env.overwriteOutput = True
# Create empty csv file

#txt = open(r"\\dataserver0\GPW\GPW4\Release_4_1\Alpha\Cartographic\tables\age_group_names.csv", "wb")

# List layers in mxd

mxd = arcpy.mapping.MapDocument(r"F:\\arcgisserver\serverdata\usgrids\sf1_2010\usgrid-summary-file1-2010-pct.mxd")  
layerList = arcpy.mapping.ListLayers(mxd)  
for layer in layerList:  
   print layer



     
     
