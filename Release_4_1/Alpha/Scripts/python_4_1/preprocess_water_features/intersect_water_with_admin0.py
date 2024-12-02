# use multiprocessing to intersect water features 
# with administrative boundaries

### THIS SCRIPT IS EXECUTRED ON DEVSEDARC4

import arcpy, os, multiprocessing, datetime

def intersect(shp):
    startTime = datetime.datetime.now()
    # define water layers to intersect
    swbd = r'D:\gpw\release_4_1\water\water_inputs\global_input_files.gdb\lakes_and_rivers_from_swbd'
    glims = r'D:\gpw\release_4_1\water\water_inputs\global_input_files.gdb\glims_glac_bound_final'
    # grab ISO
    iso = os.path.basename(shp)[:3]
    # define output files
    outSWBD = r'D:\gpw\release_4_1\water\water_inputs\intersected_swbd' + os.sep + iso + '_swbd_intersect.shp'
    outGLIMS = r'D:\gpw\release_4_1\water\water_inputs\intersected_glims' + os.sep + iso + '_glims_intersect.shp'
    try:
        arcpy.Intersect_analysis([shp,swbd], outSWBD)
        if int(arcpy.GetCount_management(outSWBD)[0])==0:
            arcpy.Delete_management(outSWBD)
    except:
        return "Failure creating: " + outSWBD, arcpy.GetMessages()
    if arcpy.Exists(outSWBD):
        arcpy.DeleteField_management(outSWBD,"FID_"+iso+"_di")
    try:
        arcpy.Intersect_analysis([shp,glims], outGLIMS)
        if int(arcpy.GetCount_management(outGLIMS)[0])==0:
            arcpy.Delete_management(outGLIMS)
    except:
        return "Failure creating: " + outGLIMS, arcpy.GetMessages()
    return "Intersected " + iso + ": " + str(datetime.datetime.now()-startTime)


def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\release_4_1\loading\admin0_shps'
    arcpy.env.workspace = inWS
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.join(inWS, fc) for fc in fcs]
##    for shp in fcList:
##        print intersect(shp)
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
    print pool.map(intersect, fcList) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)


    ## note that following this script the output SHP files were manually merged
    ## next the following countries {ALA,CAN,FIN,ISL,NOR,SJM,SWE,USA] were removed
    ## from the swbd features and replaced with data obtained from National Mapping
    ## Agencies or other local sources that were deamed more complete and accurate
    ## than the SWBD.

    ## SWDBID could be used to obtain the original SWBD features prior to intersection
    ## This might be useful if the admin0 extent for some country changes, as that could
    ## have an impact on the coverage of a given water feature if the coastline changes.

    ## NMASID could be used to obtain the original National data from the file stored on the
    ## network here: \\dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\country_outputs.gdb
    ## note that the only difference between the files in the "country_inputs" gdb versus the
    ## "county_outputs" gdb is the attributes of the source data have been removed or integrated
    ## in the outputs gdb


    ## How to choose which boundary to use?


    
if __name__ == '__main__':
    main()
