# original code adapted from grid-preprocess.py
# multiprocess_calculate_admin_areas
# calculate the administrative areas
# Kytt MacManus
# 8-28-15

# import libraries
import arcpy, os, sys, multiprocessing
import datetime
arcpy.env.overwriteOutput = True
def calculateAdminAreas(inFC):
    startTime = datetime.datetime.now()
    # check if the needed input files exist
    rootName = os.path.basename(inFC)
    iso = rootName.split("_")[0]
    waterMask = r'F:\gpw\release_4_1\water\water_outputs\water_masks' + os.sep + iso + "_water_mask.shp"
    if not arcpy.Exists(waterMask):
        hasWater = 0
    else:
        hasWater = 1
    try:
        outFolder = r'F:\gpw\release_4_1\process'
        outGDB = outFolder + os.sep + iso.lower() + ".gdb"
        if not arcpy.Exists(outGDB):
            arcpy.CreateFileGDB_management(outFolder,iso.lower()) 
        # define spatial reference
        prjFile = r'F:\gpw\custom_projections' + os.path.sep + iso[:3]+"_"+iso[3:] + "_fishnet_mollweide.prj"
        # check to see that estimates exists, if it doesn't kill the script
        if not arcpy.Exists(prjFile):
            return prjFile#"The input prj file does not exist, check the network"
        else:
            spatialRef = open(prjFile,"r").read()
            print prjFile
        templateBoundaries = r'F:\gpw\release_4_1\loading\templates.gdb\gridding_boundaries'
        # copy of inFC
        inFCG = 'in_memory' + os.sep + rootName + "_gridding"
        arcpy.CreateFeatureclass_management("in_memory",rootName + "_gridding","POLYGON",
                                            templateBoundaries,"DISABLED","DISABLED",
                                            arcpy.SpatialReference(4326))
        
        # append inFCG to outFile
        arcpy.Append_management(inFC,inFCG,"NO_TEST")
        
        # calculate the ISO field
        arcpy.CalculateField_management(inFCG,"ISO",'"' + iso.upper() + '"',"PYTHON")
        # mollweide version of fc
        projectFC = outGDB + os.sep + rootName + "_mollweide"
        waterFeatures = outGDB + os.sep + iso + "_water_features"
        waterMollweide = outGDB + os.sep + iso + "_water_features_mollweide"            
        # add a tmpid field and calculate it equal to the OBJECTID
        arcpy.AddField_management(inFCG,"TEMPID",'LONG')
        arcpy.CalculateField_management(inFCG,"TEMPID",'!OBJECTID!','PYTHON')
        # add area fields
        arcpy.AddField_management(inFCG,"ADMINAREA",'DOUBLE')
        arcpy.AddField_management(inFCG,"WATERAREA",'DOUBLE')
        arcpy.AddField_management(inFCG,"PCTABDIFF",'DOUBLE')
        arcpy.AddField_management(inFCG,"MASKEDAREA",'DOUBLE')
        # project inFCG to mollweide
        try:
            
            arcpy.Project_management(inFCG, projectFC, spatialRef)
            # add ADMINAREAKM and calculate
            arcpy.CalculateField_management(projectFC,"ADMINAREA",'!shape.area@SQUAREKILOMETERS!','PYTHON')
        except:
            return iso, arcpy.GetMessages()
        # join ADMINAREAKM to inFCG
        # create dictionary to hold values
        values = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(projectFC,["UBID","ADMINAREA"]) as rows:
                for row in rows:
                    # store with AGEID as key and a tuple of numbers as value
                    key = row[0]
                    value = row[1]
                    values[key] = value
        except:
            return "Error in " + rootName + ": Creating Value Dictionary"
        try:
            # write the values
            with arcpy.da.UpdateCursor(inFCG,["UBID","ADMINAREA"]) as rows:
                for row in rows:
                    # grab the ubid
                    ubid = row[0]
                    row[1] = values[ubid]
                    # update the row
                    rows.updateRow(row)
            # delete projectFC
            arcpy.Delete_management(projectFC)
        except:
            return "Error in " + rootName + ": Writing Value Dictionary"
        if hasWater == 1:
            # clip the boundary features to waterMask
            try:    
                arcpy.Clip_analysis(inFCG,waterMask,waterFeatures)
            except:
                return iso, arcpy.GetMessages()
            # project to mollweide and calculate WATERAREA
            try:
                arcpy.Project_management(waterFeatures, waterMollweide, spatialRef)
                arcpy.CalculateField_management(waterMollweide,"WATERAREA",'!shape.area@SQUAREKILOMETERS!','PYTHON')
            except:
                return iso, arcpy.GetMessages()
            # join WATERAREA to boundaryFeatures and to waterFeatures
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
                return "Error in " + iso + ": Creating Water Value Dictionary"
            try:
                # write the values to inFCG
                with arcpy.da.UpdateCursor(inFCG,["TEMPID","ADMINAREA","WATERAREA","PCTABDIFF","MASKEDAREA"]) as rows:
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
            except:
                return "Error in " + iso + ": Writing Water Value Dictionary"
            try:
                # write the values to waterFeatures
                with arcpy.da.UpdateCursor(waterFeatures,["TEMPID","ADMINAREA","WATERAREA"]) as rows:
                    for row in rows:
                        # grab the tmpid
                        tmpid = row[0]
                        # if the tmpid is in the values dictionary then update the row
                        if tmpid in values:
##                            return values[tmpid]
                            row[2] = values[tmpid]
                            # update the row
                            rows.updateRow(row)
                        else:
                            # otherwise
                            # update waterarea and pct difference as 0
                            row[2] = 0
                            # update the row
                            rows.updateRow(row)
                        
            except:
                return "Error in " + iso + ": Writing Water Value Dictionary to Water Features"
            # delete waterMollweide
            arcpy.Delete_management(waterMollweide)
        else:
            arcpy.CalculateField_management(inFCG,"WATERAREA",0,'PYTHON')
            arcpy.CalculateField_management(inFCG,"PCTABDIFF",0,'PYTHON')
            arcpy.CalculateField_management(inFCG,"MASKEDAREA",'!ADMINAREA!','PYTHON')
        # copy to the output file
        # make feature layer that excludes BOUNDARY_CONTEXT IS NULL and Another for Not Null, export both
        outLyr = rootName + '_null_boundary_context'
        bcLyr = rootName + "_boundary_context"
        arcpy.MakeFeatureLayer_management(inFCG,outLyr,'"'+"BOUNDARY_CONTEXT" + '" IS NULL')
        arcpy.MakeFeatureLayer_management(inFCG,bcLyr,'"'+"BOUNDARY_CONTEXT" + '" IS NOT NULL')
        outFile = outGDB + os.sep + rootName + "_gridding"
        arcpy.CopyFeatures_management(outLyr,outFile)
        if int(arcpy.GetCount_management(bcLyr)[0])<>0:
            outBoundaryContext = outGDB + os.sep + rootName + "_boundary_context"
            arcpy.CopyFeatures_management(bcLyr,outBoundaryContext)
        
        # finally select and export the items with more than 85pct change
        features2Check = r'F:\gpw\release_4_1\water\boundary_greater_than_85pct_water' + os.sep + iso + ".shp"
        threshold = 85
        whereClause = """"PCTABDIFF" >= 85"""
        try:
            arcpy.Select_analysis(outFile,features2Check,whereClause)
            if int(arcpy.GetCount_management(features2Check)[0])==0:
                   arcpy.Delete_management(features2Check)
        except:
            return iso, arcpy.GetMessages()
        
        # success
        return rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return rootName + " error: " + str(arcpy.GetMessages()) 

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'F:\gpw\release_4_1\input_data\usa.gdb'
    arcpy.env.workspace = inWS
    fcs = arcpy.ListFeatureClasses("usaak*")
    fcList = [os.path.join(inWS,fc) for fc in fcs]
    # multiprocess the data
    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
    results = pool.map(calculateAdminAreas, fcList)
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
