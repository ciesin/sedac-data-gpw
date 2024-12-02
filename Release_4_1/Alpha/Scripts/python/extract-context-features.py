# migrate input country level feature classes
# this script takes the features exported from
# sde as of some date and copies them to the
# working production features gdb based on a
# loading lookup table

# the script also isolates features with Boundary Context for review

# 9-28-2016
# Kytt MacManus

# import libraries
import os, arcpy, datetime, multiprocessing

def extractContext(fc):
    procTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    contextWS = r'D:\gpw\release_4_1\input_data\boundary_context.gdb'
    waterWS = r'D:\gpw\release_4_1\water\boundary_water_features'
    fcLyr = os.path.basename(fc) + "_lyr"
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
##    # select the boundary_context features 
##    arcpy.SelectLayerByAttribute_management(fcLyr,"NEW_SELECTION","BOUNDARY_CONTEXT IS NOT NULL")
##    # if there is more than 0 features then export
##    if int(arcpy.GetCount_management(fcLyr)[0])>0:
##        contextFile = contextWS+os.sep+os.path.basename(fc)[:3] + "_boundary_context_features"
##        arcpy.CopyFeatures_management(fcLyr,contextFile)
    arcpy.SelectLayerByAttribute_management(fcLyr,"NEW_SELECTION","BOUNDARY_CONTEXT = 7")
    # if there is more than 0 features then export
    waterFile = waterWS+os.sep+os.path.basename(fc)[:3] + "_boundary_water_features.shp"
    if int(arcpy.GetCount_management(fcLyr)[0])>0:
        arcpy.CopyFeatures_management(fcLyr,waterFile)
       
    return (waterFile,str(datetime.datetime.now() - procTime))


def main():
    
    scriptTime = datetime.datetime.now()
    datadir = r'D:\gpw\release_4_1\loading\hi_res_boundaries_10_20_16.gdb'
    arcpy.env.workspace = datadir
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.join(datadir,f) for f in fcs]
    
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
    results = pool.map(extractContext, fcList)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()




            
