# Kytt MacManus
# 10-21-16
# This Script is Executed on the Machine DEVSEDARC4
# As a prequisite the folders below must exist
# nmasWaterFeatures, boundaryWaterFeatures,
# intersectedGlims and intersectedSWBD must have been prepopulated

import arcpy, os, multiprocessing, datetime

def processCountries(iso):
    processTime = datetime.datetime.now()
    # specify the potential water files
    boundaryWaterFeatures = r'D:\gpw\release_4_1\water\water_inputs\boundary_water_features' + os.sep + iso + "_boundary_water_features.shp"
    nmasWaterFeatures = r'D:\gpw\release_4_1\water\water_inputs\nmas_water_features' + os.sep + iso + "_nmas_water_features.shp"
    intersectedGlims = r'D:\gpw\release_4_1\water\water_inputs\intersected_glims' + os.sep + iso + "_glims_intersect.shp"
    intersectedSWBD = r'D:\gpw\release_4_1\water\water_inputs\intersected_swbd' + os.sep + iso + "_swbd_intersect.shp"
    unionedBoundaryWaterFeatures = r'D:\gpw\release_4_1\water\water_outputs\unioned_boundary_water_features' + os.sep + iso + ".shp"
    unionedGLIMS = r'D:\gpw\release_4_1\water\water_outputs\unioned_glims' + os.sep + iso + ".shp"
    # output features
    maskFolder = r'D:\gpw\release_4_1\water\water_outputs\water_masks'
    finalOutputFeatures = r'D:\gpw\release_4_1\water\water_outputs\water_masks' + os.sep + iso + "_water_mask.shp"
    templateBoundaries = r'D:\gpw\release_4_1\loading\templates.gdb\water_mask'
            
    ##1) The primary water features for a given country will originate from the official water data 
    ##sources from National Mapping Agencies (NMAS) if they exist,
    if arcpy.Exists(nmasWaterFeatures):
        primaryWaterFeatures = nmasWaterFeatures
    ##otherwise the primary boundaries will originate from the SRTM SWBD. If they exist
    else:
        if arcpy.Exists(intersectedSWBD):
            primaryWaterFeatures = intersectedSWBD
        # if neither exist then just return
        else:
            return iso, 'does not have water features'
    
    ##2) The 30 countries with GLIMS data will be unioned with the primary water features. Areas of 
    ##intersection should be evaluated against imagery to determine if they represent a shift in the 
    ##feature. 
        
    ##3) There are 18 countries with Boundary Water Features. These features must be given primacy 
    ##in the water mask because any shift or overestimation of them will have a large impact on the 
    ##corresponding Country Boundaries. They will be unioned with the output from step 2 (for the 6 
    ##countries that have GLIMs and Water Boundary Features, and with the output of step 1 for the 
    ##remaining 12 countries). As in step 2, areas of intersection should be manually verified.
    try:
        # create the water mask template
        # copy
        arcpy.CreateFeatureclass_management(maskFolder,iso + "_water_mask.shp"
                                            ,"POLYGON",templateBoundaries,"DISABLED","DISABLED",
                                            arcpy.SpatialReference(4326))
            
        # copy these features to the water inputs folder only if they need no further process
        if not arcpy.Exists(intersectedGlims) and not arcpy.Exists(boundaryWaterFeatures):
            # copy
            # append 
            arcpy.Append_management(primaryWaterFeatures,finalOutputFeatures,"NO_TEST")
        # if they have no GLIMS, but do have Boundary Water Features then union them with the
        # boundary water features and copy to the union workspace
        elif not arcpy.Exists(intersectedGlims) and arcpy.Exists(boundaryWaterFeatures) and not arcpy.Exists(unionedBoundaryWaterFeatures):
            # union
            arcpy.Union_analysis([[boundaryWaterFeatures,1],[primaryWaterFeatures,2]],unionedBoundaryWaterFeatures,
                                 "ALL","#","GAPS")
            # append 
            arcpy.Append_management(unionedBoundaryWaterFeatures,finalOutputFeatures,"NO_TEST")

        # if they have GLIMS but no Boundary Water Features then union them with the glims
        # and copy to the union workspace
        elif arcpy.Exists(intersectedGlims) and not arcpy.Exists(boundaryWaterFeatures) and not arcpy.Exists(unionedGLIMS):
            # union
            arcpy.Union_analysis([[primaryWaterFeatures,1],[intersectedGlims,2]],unionedGLIMS,
                                 "ALL","#","GAPS")
            # append 
            arcpy.Append_management(unionedGLIMS,finalOutputFeatures,"NO_TEST")
        # finally, if they have both features then union with both and add to the union workspace
        elif arcpy.Exists(intersectedGlims) and arcpy.Exists(boundaryWaterFeatures) and not arcpy.Exists(unionedBoundaryWaterFeatures):
            # union
            arcpy.Union_analysis([[boundaryWaterFeatures,1],[primaryWaterFeatures,2],[intersectedGlims,3]],unionedBoundaryWaterFeatures,
                                 "ALL","#","GAPS")
            # append 
            arcpy.Append_management(unionedBoundaryWaterFeatures,finalOutputFeatures,"NO_TEST")
        # calculate the ISO field
        arcpy.CalculateField_management(finalOutputFeatures,"ISO",'"' + iso.upper() + '"',"PYTHON")
        return iso, str(datetime.datetime.now()-processTime)
    
    except:
        return iso, arcpy.GetMessages()
def main():
    scriptTime = datetime.datetime.now()
    datadir = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
    arcpy.env.workspace = datadir
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.basename(f)[:3] for f in fcs]
    # add US
    fcList.append('usa')
    fcList.sort()
##    print fcList
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=25,maxtasksperchild=1)
    results = pool.map(processCountries, fcList)
    for r in results:
        print r
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
