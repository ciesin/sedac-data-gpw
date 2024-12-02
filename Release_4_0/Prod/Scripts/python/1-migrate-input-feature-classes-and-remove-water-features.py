# migrate input country level feature classes
# this script takes the beta features from sde
# \\Dataserver0\gpw\GPW4\Release_4_0\Beta\Gridding\global\features\from_sde\country_boundaries_hi_res.gdb
# and copies them to the working production features gdb
# \\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\from_sde\country_boundaries_hi_res.gdb

# the script also removes features in the boundaries which represent water
# those features are or should already be present in the water mask and because
# the treatment of water features varies between countries in the input data
# eg some countries include water as features and others do not
# we need to purge the water features from all countries and revise the water mask where appropriate

# 2-3-2016
# Kytt MacManus

# import libraries
import arcpy, os,datetime

# define input and output directories
inWS = r'D:\gpw\beta\country_boundaries_hi_res.gdb'
outWS = r'D:\gpw\country_boundaries_hi_res.gdb'

# set working directory to inWS
arcpy.env.workspace = inWS

# create list of fcs
fcs = arcpy.ListFeatureClasses("*")
fcs.sort()
for fc in fcs:
    processTime = datetime.datetime.now()
    # derive iso
    iso = fc[:3]
    print "processing " + iso
    # first create feature layer
    fcLyr = fc + "_lyr"
    arcpy.MakeFeatureLayer_management(fc,fcLyr)
    # make selection
    arcpy.SelectLayerByAttribute_management(fcLyr,"NEW_SELECTION","BOUNDARY_CONTEXT <> 7 OR BOUNDARY_CONTEXT IS NULL")
    # finally copy the features
    arcpy.CopyFeatures_management(fcLyr,outWS+os.sep+fc)
    print datetime.datetime.now()-processTime


            
