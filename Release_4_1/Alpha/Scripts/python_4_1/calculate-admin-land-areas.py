# original code adapted from grid-preprocess.py
# multiprocess_calculate_admin_areas
# calculate the administrative areas
# Kytt MacManus
# 8-28-15

# import libraries
import arcpy, os, sys, multiprocessing
import datetime

def calculateAdminAreas(inFC):
    startTime = datetime.datetime.now()
    try:
        arcpy.env.overwriteOutput = True
        rootName = os.path.basename(inFC)
        iso = rootName[:3]
        # define spatial reference
        prjFile = r'D:\gpw\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
        # check to see that estimates exists, if it doesn't kill the script
        if not arcpy.Exists(prjFile):
            print "The input prj file does not exist, check the network"
        else:
            spatialRef = open(prjFile,"r").read()
            print prjFile
        # copy of inFC
        inFCG = 'in_memory' + os.sep + rootName + "_gridding"
        arcpy.CopyFeatures_management(inFC,inFCG)
        # tmpid field
        tmpid = "TEMPID"
        # mollweide version of fc
        projectFC = r'D:\gpw\release_4_1\loading\hi_res_boundaries_mollweide' + os.sep + rootName + "_mollweide.shp"
        # calculate adminArea 
        adminArea = "ADMINAREA"              
        # add a tmpid field and calculate it equal to the OBJECTID
        arcpy.AddField_management(inFCG,adminArea,'DOUBLE')
        arcpy.AddField_management(inFCG,tmpid,'TEXT')
        arcpy.CalculateField_management(inFCG,tmpid,'!OBJECTID!','PYTHON')
        # project inFCG to mollweide
        arcpy.Project_management(inFCG, projectFC, spatialRef)   
        # add ADMINAREAKM and calculate
        arcpy.CalculateField_management(projectFC,adminArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
        # join ADMINAREAKM to inFCG
        # create dictionary to hold values
        values = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(projectFC,["UBID",adminArea]) as rows:
                for row in rows:
                    # store with AGEID as key and a tuple of numbers as value
                    key = row[0]
                    value = row[1]
                    values[key] = value
        except:
            return "Error in " + rootName + ": Creating Value Dictionary"
        try:
            # write the values
            with arcpy.da.UpdateCursor(inFCG,["UBID",adminArea]) as rows:
                for row in rows:
                    # grab the ubid
                    ubid = row[0]
                    row[1] = values[ubid]
                    # update the row
                    rows.updateRow(row)
        except:
            return "Error in " + rootName + ": Writing Value Dictionary"
        
        # finally copy to the output file
        outFile = r'D:\gpw\release_4_1\loading\hi_res_boundaries_with_area_calcs' + os.sep + rootName + ".shp"
        arcpy.CopyFeatures_management(inFCG,outFile)
        # success
        return rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return rootName + " error: " + str(arcpy.GetMessages()) 

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\release_4_1\loading\hi_res_boundaries_10_20_16.gdb'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.join(inWS,fc) for fc in fcs]
##    for fc in fcList:
##        print fc
##        print calculateAdminAreas(fc)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    print pool.map(calculateAdminAreas, fcList) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
