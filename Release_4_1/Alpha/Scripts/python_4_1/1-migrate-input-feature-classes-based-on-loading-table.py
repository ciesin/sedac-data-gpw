# migrate input country level feature classes
# this script takes the features exported from
# sde as of some date and copies them to the
# working production features gdb based on a
# loading lookup table

# the script also isolates features with Boundary Context for review

# 9-28-2016
# Kytt MacManus

# import libraries
import arcpy, os,datetime

# define input and output directories
inWS = r'D:\gpw\release_4_1\loading\sde_export_11_17_16.gdb'
outWS = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
contextWS = r'D:\gpw\release_4_1\input_data\boundary_context.gdb'
waterWS = r'D:\gpw\release_4_1\input_data\water_context.gdb'
# set working directory to inWS
arcpy.env.workspace = inWS

# define input table
loadingTbl = r'D:\gpw\release_4_1\loading\loading_table.gdb\loading_11_17_16'

# read the ISO field from loadingTbl
with arcpy.da.SearchCursor(loadingTbl,"ISO") as rows:
    for row in rows:
        processTime = datetime.datetime.now()
        # parse ISO
        iso =row[0]
########        print iso
######        checkFile = r'D:\gpw\release_4_1\loading\admin0_shps' +os.sep+iso+".shp"
######        if not arcpy.Exists(checkFile):
######            fc = arcpy.ListFeatureClasses(iso+"*" + "boundaries_2010")[0]
######            arcpy.Dissolve_management(fc,checkFile)
######            print checkFile
            
        if iso == 'USA':
            continue
        # grab the feature class
        fc = arcpy.ListFeatureClasses(iso+"*" + "boundaries_2010")[0]
        fcLyr = fc + "_lyr"
        outFile = outWS+os.sep+fc
##        if arcpy.Exists(outFile):
##            continue
        # parse the field info
        field_info_str = ''
        input_fields = arcpy.ListFields(fc)
        keep_fields_list = ["OBJECTID","SHAPE","GUBID","UBID","ISO","BOUNDARY_CONTEXT"]
        for field in input_fields:
            if field.name in keep_fields_list:
                field_info_str += field.name + ' ' + field.name + ' VISIBLE;'
            else:
                field_info_str += field.name + ' ' + field.name + ' HIDDEN;'
        field_info_str = field_info_str.rstrip(';')  # Remove trailing semicolon
        # first create feature layer        
        arcpy.MakeFeatureLayer_management(fc,fcLyr,"#","#",field_info_str)
        # finally copy the features
        arcpy.CopyFeatures_management(fcLyr,outFile)
        # select the boundary_context features 
        arcpy.SelectLayerByAttribute_management(fcLyr,"NEW_SELECTION","BOUNDARY_CONTEXT IS NOT NULL")
        # if there is more than 0 features then export
        if int(arcpy.GetCount_management(fcLyr)[0])>0:
            contextFile = contextWS+os.sep+fc
            arcpy.CopyFeatures_management(fcLyr,contextFile)
        # select the water_context features 
        arcpy.SelectLayerByAttribute_management(fcLyr,"NEW_SELECTION","BOUNDARY_CONTEXT = 7")
        # if there is more than 0 features then export
        if int(arcpy.GetCount_management(fcLyr)[0])>0:
            waterFile = waterWS+os.sep+fc
            arcpy.CopyFeatures_management(fcLyr,waterFile)
        print "Created " + outFile
        print datetime.datetime.now()-processTime
##       

            
