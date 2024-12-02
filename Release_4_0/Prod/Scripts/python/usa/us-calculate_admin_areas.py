# original code adapted from grid-preprocess.py
# multiprocess_calculate_admin_areas
# calculate the administrative areas
# Kytt MacManus
# 8-28-15

# import libraries
import arcpy, os, sys, multiprocessing
import datetime

def calculateAdminAreas(gdb):
    startTime = datetime.datetime.now()
    try:
        arcpy.env.overwriteOutput = True
        # these variables must all be parsed from input gdb        
        # define inputs
        gdbName = os.path.basename(gdb)
        rootName = os.path.basename(gdb).replace(".gdb","")
        # grab inFC
        boundaryWS = r'H:\gpw\us_boundaries_hi_res.gdb'
        arcpy.env.workspace = boundaryWS                                    
        inFC = boundaryWS + os.sep + str(arcpy.ListFeatureClasses(rootName + "*")[0])
        print inFC
        workspace = gdb
        # define spatial reference
        prjFile = r'H:\gpw\custom_projections' + os.path.sep + rootName + "_fishnet_mollweide.prj"
        # check to see that estimates exists, if it doesn't kill the script
        if not arcpy.Exists(prjFile):
            print "The input prj file does not exist, check the network"
        else:
            spatialRef = open(prjFile,"r").read()
            print prjFile
        # define gridding resolution
        # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
        # 1 degree divided into 120 parts is 30 seconds
        linespd = 120
        # copy of inFC
        inFCG = gdb + os.sep + rootName + "_gridding"
        arcpy.Copy_management(inFC,inFCG)
        # tmpid field
        tmpid = "TEMPID"
        # mollweide version of fc
        projectFC = gdb + os.sep + rootName + "_mollweide"
        # calculated adminArea 
        adminArea = "ADMINAREAKM"
        maskedArea = "ADMINAREAKMMASKED"
        adminWaterArea = "ADMINWATERAREAKM"
        
        # define workspace environment
        arcpy.env.workspace = workspace              
        # add a tmpid field and calculate it equal to the OBJECTID
        arcpy.AddField_management(inFCG,adminArea,'DOUBLE')
        arcpy.AddField_management(inFCG,adminWaterArea,'DOUBLE')
        arcpy.CalculateField_management(inFCG,adminWaterArea,0,'PYTHON')
        arcpy.AddField_management(inFCG,maskedArea,'DOUBLE')
        arcpy.AddField_management(inFCG,tmpid,'TEXT')
        arcpy.CalculateField_management(inFCG,tmpid,'!UBID!','PYTHON')
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
            return "Error in " + gdbName + ": Creating Value Dictionary"
        try:
            # read the values
            with arcpy.da.UpdateCursor(inFCG,["UBID",adminArea]) as rows:
                for row in rows:
                    # grab the ubid
                    ubid = row[0]
                    row[1] = values[ubid]
                    # update the row
                    rows.updateRow(row)
            arcpy.CalculateField_management(inFCG,maskedArea,'!' + adminArea + '! - !' + adminWaterArea + "!",'PYTHON')
        except:
            return "Error in " + gdbName + ": Writing Value Dictionary"
        
        # success
        return "Calculated Areas for " + gdbName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return gdbName + " error: " + str(arcpy.GetMessages())


    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'H:\gpw\pop_tables'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("*")
    workspaces.sort()
    gdb_list = []
    for workspace in workspaces:
        # describe the workspace
        workDesc = arcpy.Describe(workspace)
        # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
        if str(workDesc.workspaceType)=="FileSystem":
            workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
        gdb_list.append(workspace) 
##    for gdb in gdb_list:
##        print gdb
##        print calculateAdminAreas(gdb)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
    print pool.map(calculateAdminAreas, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
