# GPW Gridding
# Purpose: To proportionally allocate demographic variables to grid cells
# Kytt MacManus
# August 23, 2012

# Import Python Libraries
import arcpy, os
from arcpy import env

# Set Overwrite Output Environment
env.overwriteOutput = 1

# Define Workspace Variable
workspace = r'F:\gpw\BMU\BMU.gdb'

# Set Workspace and Scratch Workspace Environments
env.workspace = workspace
env.scratchworkspace = workspace

# Create Feature Class List
fcs = arcpy.ListFeatureClasses("bmu_2010")
#Iterate
for fc in fcs:
    print "Processing " + fc
### This section is adapted form calcareas.py as written
### by Greg Yetman circa 2010
    # Error catch: make sure it is a featureclass, type = polygon, and is in WGS84
    desc = arcpy.Describe(fc)
    if desc.dataType != 'FeatureClass':
        print 'Input data type is not a feature class!'
        raise Exception()
    else:
        pass
    if desc.shapeType != 'Polygon':
        print 'Input feature class must be a polygon feature class'
        raise Exception()
    else:
        pass
    spatialRef = desc.spatialReference.name
    if spatialRef != 'GCS_WGS_1984':
        print 'Input feature class projection undefined or not WGS84!'
        raise Exception()
    else:
        pass
    
    
