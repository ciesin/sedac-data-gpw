# Name: FeatureClassToFeatureClass_Example2.py
# Description: Use FeatureClassToFeatureClass with an expression to create a subset
#  of the original feature class.  
 
# Import system modules
import arcpy
from arcpy import env
 
# Set environment settings
env.workspace = r'C:\jsquires_work'
 
# Set local variables
inFeatures = "fin_admin2_2010_NEW.shp"
outLocation = r'C:\jsquires_work\boundary_adjustment.gdb'
outFeatureClass = "fin_admin2_2010_NEW.shp"

# Execute FeatureClassToFeatureClass
arcpy.FeatureClassToFeatureClass_conversion(inFeatures, outLocation, outFeatureClass)
print outFeatureClass + " is copied"
print "done"

