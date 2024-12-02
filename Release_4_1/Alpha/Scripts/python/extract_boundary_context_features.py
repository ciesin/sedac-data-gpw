# Kytt MacManus

# import libraries
import arcpy, os,datetime

# define input and output directories
inWS = r'D:\gpw\country_boundaries_hi_res.gdb'
outWS = r'D:\gpw\data_quality.gdb'

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
    arcpy.SelectLayerByAttribute_management(fcLyr,"NEW_SELECTION","BOUNDARY_CONTEXT IS NOT NULL")
    if int(arcpy.GetCount_management(fcLyr)[0])==0:
        print datetime.datetime.now()-processTime
    else:
        # finally copy the features
        arcpy.CopyFeatures_management(fcLyr,outWS+os.sep+fc.replace("2010","context_features"))
        print "Created " + fc.replace("2010","context_features")
        print datetime.datetime.now()-processTime


            
