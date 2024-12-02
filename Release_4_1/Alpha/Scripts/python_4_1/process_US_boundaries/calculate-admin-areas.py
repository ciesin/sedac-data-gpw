# original code adapted from grid-preprocess.py
# multiprocess_calculate_admin_areas
# calculate the administrative areas
# Kytt MacManus
# 8-28-15

# import libraries
import arcpy, os
import datetime
arcpy.env.overwriteOutput = True

outGDB = r'F:\GPW\us_boundaries_working\water_working.gdb'
waterMasks = r'F:\GPW\us_boundaries_working\water_masks_usa.gdb'
inGDB = r'F:\GPW\us_boundaries_working\usa_boundaries_hi_res.gdb'
projections = r'F:\GPW\us_boundaries_working\custom_projections'

arcpy.env.workspace = inGDB
fcList = arcpy.ListFeatureClasses()

fields = ['STATEFP10','COUNTYFP10','TRACTCE10','BLOCKCE10','GEOID10','NAME10',
          'MTFCC10','UR10','UACE10','UATYP10','FUNCSTAT10','ALAND10','AWATER10',
          'INTPTLAT10','INTPTLON10']

for inFC in fcList[2:]:
    iso = inFC[:6]
    print iso
    
    # define spatial reference
    prjFile = os.path.join(projections,iso+'_fishnet_mollweide.prj')
    spatialRef = open(prjFile,"r").read()

    # mollweide version of fc
    projectFC = outGDB + os.sep + iso + "_mollweide"
    waterMask = os.path.join(waterMasks,iso+'_water_mask')
    waterFeatures = os.path.join(outGDB,iso+'_water_mask')
    waterMollweide = os.path.join(outGDB,iso+"_water_mask_mollweide")
    # add area fields
    arcpy.AddField_management(inFC,"ADMINAREA",'DOUBLE')
    arcpy.AddField_management(inFC,"WATERAREA",'DOUBLE')
    arcpy.AddField_management(inFC,"PCTABDIFF",'DOUBLE')
    arcpy.AddField_management(inFC,"MASKEDAREA",'DOUBLE')
    # project inFCG to mollweide
    print "setup is done"
    arcpy.Project_management(inFC, projectFC, spatialRef)
    # add ADMINAREAKM and calculate
    arcpy.CalculateField_management(projectFC,"ADMINAREA",'!shape.area@SQUAREKILOMETERS!','PYTHON')

    # join ADMINAREAKM to inFCG
    # create dictionary to hold values
    values = {}
    # read the values
    with arcpy.da.SearchCursor(projectFC,["UBID","ADMINAREA"]) as rows:
        for row in rows:
            # store with AGEID as key and a tuple of numbers as value
            key = row[0]
            value = row[1]
            values[key] = value
    # write the values
    with arcpy.da.UpdateCursor(inFC,["UBID","ADMINAREA"]) as rows:
        for row in rows:
            # grab the ubid
            ubid = row[0]
            row[1] = values[ubid]
            # update the row
            rows.updateRow(row)
    print "calculated admin area"
    # delete projectFC
    arcpy.Delete_management(projectFC)

    # clip the boundary features to waterMask
    arcpy.Clip_analysis(inFC,waterMask,waterFeatures)

    # project to mollweide and calculate WATERAREA
    arcpy.Project_management(waterFeatures, waterMollweide, spatialRef)
    arcpy.CalculateField_management(waterMollweide,"WATERAREA",'!shape.area@SQUAREKILOMETERS!','PYTHON')

    # join WATERAREA to boundaryFeatures
    # create dictionary to hold values
    values = {}
    # read the values
    with arcpy.da.SearchCursor(waterMollweide,["UBID","WATERAREA"]) as rows:
        for row in rows:
            # store with TMPID as key the summed waterarea as the value
            key = row[0]
            if key in values:
                value += row[1]
            else:
                value = row[1]
            values[key] = value
            
    # write the values
    with arcpy.da.UpdateCursor(inFC,["UBID","ADMINAREA","WATERAREA","PCTABDIFF","MASKEDAREA"]) as rows:
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
                # otherwise
                # update waterarea and pct difference as 0
                row[2] = 0
                row[3] = 0
                # update the maskedarea as = adminarea
                row[4] = row[1]
                # update the row
                rows.updateRow(row)
                
    # delete waterMollweide
    arcpy.Delete_management(waterMollweide)

    print "did some stuff"
    # copy to the output file
    outFile = outGDB + os.sep + iso + "_water_gridding"
    arcpy.CopyFeatures_management(inFC,outFile)
    # finally select and export the items with more than 85pct change
    features2Check = os.path.join(r'F:\GPW\us_boundaries_working\water_units_to_check.gdb',iso+'_to_check')
    threshold = 85

    arcpy.Select_analysis(outFile,features2Check,"PCTABDIFF >= 85 AND ATOTPOPBT > 0")
    if int(arcpy.GetCount_management(features2Check)[0])==0:
        arcpy.Delete_management(features2Check)
    else:
        arcpy.DeleteField_management(features2Check,fields)
    print "done"

