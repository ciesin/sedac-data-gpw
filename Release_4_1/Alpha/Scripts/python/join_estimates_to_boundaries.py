
# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing

def joinEstimates(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-4]
    try:
        arcpy.env.workspace = gdb
        # grab inputs
        estimatesTable = arcpy.ListTables("*_estimates")[0]
        griddingBoundaries = arcpy.ListFeatureClasses("*_gridding")[0]

        
        # read the boundaries into memory
        memBoundaries = 'in_memory' + os.sep + os.path.basename(griddingBoundaries) + "_view"
        try:
            arcpy.CopyFeatures_management(griddingBoundaries,memBoundaries)
        except:
            return "Error in " + rootName + " : making fishnet in memory"
        # define initial list of searchFields
        searchFields = ["UBID"]
        updateFields = ["UBID"]
        # create list of variables
        variables = arcpy.ListFields(estimatesTable,"*")
        for variable in variables:
            name = variable.name
            if name == "OBJECTID":
                continue
            if name == "UBID":
                continue
            elif name == "ADMINAREAKMMASKED":
                continue
            else:
                newField =  name
                fType = variable.type
            
            # add the field
            arcpy.AddField_management(memBoundaries,newField,fType)
            # append the newField to updateFields, and the variable.name to searchFields
            updateFields.append(newField)
            searchFields.append(name)
        # create dictionary to hold source counts
        counts = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(estimatesTable,searchFields) as rows:
                for row in rows:
                    # store with PIXELID as key and a tuple of estimates as value
                    pixelid = row[0]
                    value = row
                    counts[pixelid] = value
        except:
            return "Error in " + rootName + ": Creating Counts Dictionary"
        # write the density estimates to estimatesFile
        try:
            # read the values
            with arcpy.da.UpdateCursor(memBoundaries,updateFields) as rows:
                for row in rows:
                    # grab the pixelid
                    pixelid = row[0]
                    if pixelid not in counts:
                        continue
                    # set the fields
                    i = 0
                    for field in updateFields:
                        if i < 1:
                            i = i + 1                            
                            pass
                        else:
                            # calculate the counts
                            row[i]= counts[pixelid][i]

                            i = i + 1
                    
                    # update the row                    
                    rows.updateRow(row)
                    
                    
        except:
            return "Error in " + rootName + ": Writing Updates"
        return memBoundaries
    except:
        return rootName + " error: " + str(arcpy.GetMessages())
def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\pop_tables'
    outGDB = r'D:\gpw\boundaries_used_for_gridding.gdb'
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
            workspace = workspace + os.sep + os.path.basename(workspace) + ".gdb"
##            arcpy.env.workspace = workspace
##            gdbs = arcpy.ListWorkspaces("*")
##            for gdb in gdbs:
##                gdb_list.append(gdb)
            gdb_list.append(workspace)
        else:
            gdb_list.append(workspace) 
    for gdb in gdb_list:
        result = joinEstimates(gdb)
        # finally write the final fishnet
        try:
            outBoundaries = outGDB + os.sep + os.path.basename(result)[:-5]
            arcpy.CopyFeatures_management(result,outBoundaries)
            # success
            print "Transferred fields for " + os.path.basename(result)[:-5]
        except:
            print "Error in " + result + ": " + str(arcpy.GetMessages())
        
        
    # multiprocess the data
##    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
##    results = pool.map(joinEstimates, gdb_list)
##    print results
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()

##    for result in results:
##        # finally write the final fishnet
##        try:
##            outBoundaries = outGDB + os.sep + os.path.basename(result)[:-5]
##            print outBoundaries
##            arcpy.CopyFeatures_management(result,outBoundaries)
##            # success
##            print "Transferred fields for " + os.path.basename(result)[:-5]
##        except:
##            print "Error in " + result + ": " + str(arcpy.GetMessages())
        
        
        
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()

### Kytt MacManus
##
### import libraries
##import arcpy, os,datetime
##
### define input and output directories
##inWS = r'D:\gpw\country_boundaries_hi_res.gdb'
##outWS = r'D:\gpw\data_quality.gdb'
##
### set working directory to inWS
##arcpy.env.workspace = inWS
##
### create list of fcs
##fcs = arcpy.ListFeatureClasses("*")
##fcs.sort()
##for fc in fcs:
##    processTime = datetime.datetime.now()
##    # derive iso
##    iso = fc[:3]
##    print "processing " + iso
##    # first create feature layer
##    fcLyr = fc + "_lyr"
##    arcpy.MakeFeatureLayer_management(fc,fcLyr)
##    # make selection
##    arcpy.SelectLayerByAttribute_management(fcLyr,"NEW_SELECTION","BOUNDARY_CONTEXT IS NOT NULL")
##    if int(arcpy.GetCount_management(fcLyr)[0])==0:
##        print datetime.datetime.now()-processTime
##    else:
##        # finally copy the features
##        arcpy.CopyFeatures_management(fcLyr,outWS+os.sep+fc.replace("2010","context_features"))
##        print "Created " + fc.replace("2010","context_features")
##        print datetime.datetime.now()-processTime
