# Kytt MacManus
# 10-21-16
##4) A Water Mask for a given country (generated in Task 1)
##will be used to clip its corresponding Country Boundaries. 
##Land areas will then be recalculated on the clip result such that TMPID shared with the 
##original Country Boundaries and the clip can be used to join the new area values to the 
##original Country Boundaries. The percent difference in area from the original Country Boundary 
##calculations compared to the recalculated land areas from the clip result. A threshold will be 
##applied to determine which intersecting units require quality assurance. 
##
##5) Items greater than some percentage threshold should be manually evaluated to determine how 
##best to correct the Water Mask. In many cases the impacted boundary feature could be erased 
##from the Water Mask as a correction. However, in some cases the Water Mask feature could be 
##valid but shifted, so each case should also be compared to imagery. If it turns out the 
##boundaries are shifted we will evaluate case by case.  QAQC, not automated.
# prerequisites
# Land areas for the Country Boundaries will need to have been calculated.

import arcpy, os, multiprocessing, datetime

def processCountries(waterMask):
    arcpy.env.overwriteOutput=True
    processTime = datetime.datetime.now()
    iso = os.path.basename(waterMask)[:3]
    # define spatial reference
    prjFile = r'D:\gpw\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
    # check to see that estimates exists, if it doesn't kill the script
    if not arcpy.Exists(prjFile):
        print "The input prj file does not exist, check the network"
    else:
        spatialRef = open(prjFile,"r").read()
    # specify the potential water files
    waterFeatures = r'D:\gpw\release_4_1\water\water_features' + os.sep + iso + "_water_features.shp"
    waterMollweide = r'D:\gpw\release_4_1\water\water_features_mollweide'+ os.sep + iso + "_water_features_mollweide.shp"
    features2Check = r'D:\gpw\release_4_1\water\boundary_greater_than_85pct_water' + os.sep + iso + ".shp"
    # grab the boundary feature if they exist
    try:
        arcpy.env.workspace = r'D:\gpw\release_4_1\loading\hi_res_boundaries_with_area_calcs'
        boundaryFeatures = arcpy.ListFeatureClasses(iso+"*")[0]
        # add the area calculation fields
        arcpy.AddField_management(boundaryFeatures,"WATERAREA",'DOUBLE')
        arcpy.AddField_management(boundaryFeatures,"PCTABDIFF",'DOUBLE')
        arcpy.AddField_management(boundaryFeatures,"MASKEDAREA",'DOUBLE')
    except:
        return iso, "boundaries do not exist, check workspace", arcpy.GetMessages()
    # clip the boundary features to waterMask
    try:    
        arcpy.Clip_analysis(boundaryFeatures,waterMask,waterFeatures)
    except:
        return iso, arcpy.GetMessages()
    # project to mollweide and calculate WATERAREA
    try:
        arcpy.Project_management(waterFeatures, waterMollweide, spatialRef)
        arcpy.CalculateField_management(waterMollweide,"WATERAREA",'!shape.area@SQUAREKILOMETERS!','PYTHON')
    except:
        return iso, arcpy.GetMessages()
    # join WATERAREA to boundaryFeatures
    # create dictionary to hold values
    values = {}
    try:
        # read the values
        with arcpy.da.SearchCursor(waterMollweide,["TEMPID","WATERAREA"]) as rows:
            for row in rows:
                # store with TMPID as key the summed waterarea as the value
                key = row[0]
                if key in values:
                    value += row[1]
                else:
                    value = row[1]
                values[key] = value
    except:
        return "Error in " + iso + ": Creating Value Dictionary"
    try:
        # write the values
        with arcpy.da.UpdateCursor(boundaryFeatures,["TEMPID","ADMINAREA","WATERAREA","PCTABDIFF","MASKEDAREA"]) as rows:
            for row in rows:
                # grab the tmpid
                tmpid = row[0]
                # if the tmpid is in the values dictionary then update the row
                if tmpid in values:
                    row[2] = values[tmpid]
                    # calculate maskedarea
                    row[4] = row[1] - row[2]
                    if row[4] < 0:
                        row[4] = 0
                    # calculate the absolute value of the pct difference
                    row[3] = abs(((row[1]-row[4])/row[1])*100)
                    # update the row
                    rows.updateRow(row)
                else:
                    # otherwise just update the maskedarea as = adminarea
                    row[4] = row[1]
                    # update the row
                    rows.updateRow(row)
                
    except:
        return "Error in " + iso + ": Writing Value Dictionary"
    
    # finally select and export the items with more than 85pct change
    threshold = 85
    whereClause = """"PCTABDIFF" >= 85"""
    try:
        arcpy.Select_analysis(boundaryFeatures,features2Check,whereClause)
        if int(arcpy.GetCount_management(features2Check)[0])==0:
               arcpy.Delete_management(features2Check)
    except:
        return iso, arcpy.GetMessages()
    # success
    return iso + ": " + str(datetime.datetime.now()-processTime)
def main():
    scriptTime = datetime.datetime.now()
    datadir = r'D:\gpw\release_4_1\water\water_masks'
    arcpy.env.workspace = datadir
    fcs = arcpy.ListFeatureClasses("esh*")
    fcList = [os.path.join(datadir,f) for f in fcs]
    fcList.sort()
    
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(processCountries, fcList)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
