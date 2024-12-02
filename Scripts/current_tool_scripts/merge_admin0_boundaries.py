
# merge_rasters.py
# script to merge country rasters into global raster

# import libraries
import os, arcpy, datetime

# set counter
startTime = datetime.datetime.now()

# Check out Spatial Analyst
arcpy.CheckOutExtension("SPATIAL")

ws = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\boundaries_admin0.gdb'
arcpy.env.workspace = ws

fcList = arcpy.ListFeatureClasses("*")
arcpy.Merge_management(fcList, "Merge")
                    

print datetime.datetime.now()-startTime
arcpy.AddMessage(datetime.datetime.now()-startTime)
     
