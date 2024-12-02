# add GADM2 to inputData
# set up preprocessing folders
# Kytt MacManus
# July 1, 2014

# import libraries
import os, arcpy, sys
import datetime
# set counter
startTime = datetime.datetime.now()
# define workspace
gadmAdminWS = r'\\Dataserver0\gpw\GPW4\Preprocessing\Global\AdministrativeBoundaries\gadm2_country.gdb'
inputRoot = r'\\Dataserver0\gpw\GPW4\InputData\Country'
# set env.workspace
arcpy.env.workspace = gadmAdminWS
# list feature classes
fcs = arcpy.ListFeatureClasses("*")
# iterate
for fc in fcs:
    countryFolder = inputRoot + os.sep + fc
    if not arcpy.Exists(countryFolder):
        print fc + " is missing country folder"
        arcpy.CreateFolder_management(inputRoot,fc)        
        arcpy.CreateFolder_management(countryFolder,"boundary")
        arcpy.CreateFolder_management(countryFolder,"census")
        print "Created " + inputRoot + os.sep + fc
    else:
        boundaryFolder = countryFolder + os.sep + "boundary"
        if not arcpy.Exists(boundaryFolder):
            print fc + " is missing boundary folder"
    
    boundaryFolder = countryFolder + os.sep + "boundary"
    gadmFolder = boundaryFolder + os.sep + "GADM2"
    # create folder for GADM2 Data
    if not arcpy.Exists(gadmFolder):
        arcpy.CreateFolder_management(boundaryFolder,"GADM2")

    # create fileGDB to copy GADM2 into
    gadmGDB = gadmFolder + os.sep + fc + "_gadm.gdb"
    if not arcpy.Exists(gadmGDB):
        arcpy.CreateFileGDB_management(gadmFolder,fc + "_gadm")
        print "Created " + gadmGDB

    # copy files to gdb
    outFC = gadmGDB + os.sep + fc
    outSHP = gadmFolder + os.sep + fc + ".shp"

    if not arcpy.Exists(outFC):
        arcpy.CopyFeatures_management(fc,outFC)
        print "Created " + outFC
    if not arcpy.Exists(outSHP):
        arcpy.FeatureClassToFeatureClass_conversion(fc,gadmFolder,fc)
        print "Created " + outSHP
