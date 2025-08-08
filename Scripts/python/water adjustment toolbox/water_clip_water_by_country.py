import os 
import arcpy

framework_gdb = r'Z:\GPW\GPW5\Preprocessing\Global\framework_boundaries\gpwv5_level0_framework_boundaries.gdb'
output_folder = r'Z:\GPW\GPW5\Preprocessing\Global\Water\country'
water_global_fc = r'F:\gpwv5\water\water_ingest.gdb\water_MultiToSingle_FINAL'

arcpy.env.workspace = framework_gdb

framework_list = arcpy.ListFeatureClasses('GBNIR*')

for fc in framework_list:
    output_gdb = os.path.join(output_folder, fc + ".gdb")
    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(output_folder, fc + ".gdb")
         # Set the output path for the clipped feature class
        clipped_output = os.path.join(output_gdb, fc+"_water")
        # Clip the water_global feature class with the current feature class (fc)
        arcpy.Clip_analysis(water_global_fc, fc, clipped_output)
        print(fc)
    
    else:
        continue