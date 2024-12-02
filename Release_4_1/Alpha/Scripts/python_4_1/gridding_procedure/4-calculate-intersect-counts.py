# multiprocess template
import os, datetime, socket
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def tableToDict(table,searchFields):
    values = {}
    # read the values
    with arcpy.da.SearchCursor(table,searchFields) as rows:
        for row in rows:
            # store with UBID as key and a tuple of numbers as value
            key = row[0]
            value = row
            values[key] = value
    return values
    
def process(outGDB):
    arcpy.env.overwriteOutput = True
    processTime = datetime.datetime.now()
    iso = os.path.basename(outGDB)[:3]
    rootName = os.path.basename(outGDB)[:-4]
    try:
        arcpy.env.workspace = outGDB
        inPop = arcpy.ListTables("*estimates")
        if len(inPop)==0:
            return outGDB + " estimates file is missing"
        else:
            estimatesFile = inPop[0]
        intersectedFishnets = arcpy.ListFeatureClasses("*_intersect")
        if len(intersectedFishnets)==0:
            return outGDB + " intersected fishnet is missing"
        else:
            intersectedFishnet = intersectedFishnets[0]
        try:
            memFishnet = 'in_memory' + os.sep + rootName + "_view"
            arcpy.CopyRows_management(intersectedFishnet,memFishnet)
        except:
            return "Error in " + rootName + " : making table views"
        # grab the centroids data in order to get context
        if iso == "usa":
            centFile =  r'D:\gpw\release_4_1\input_data\centroids\country_data.gdb' + os.sep + iso + rootName[3:5] + "_centroids"
        else:
            centFile = r'D:\gpw\release_4_1\input_data\centroids\country_data.gdb' + os.sep + iso + "_centroids"
        if not arcpy.Exists(centFile):
            return "ERROR " + centFile + " is missing"
        # read estimates into memory
        try:
            centFields = ["UBID","CONTEXT"]
            contexts = tableToDict(centFile,centFields)
        except:
            return "Error in " + iso + ": Creating Centroids Dictionary"
        # create list of variables
        searchFields = ["UBID","MASKEDADMINAREA"]
        arcpy.AddField_management(memFishnet,"MASKEDADMINAREA","DOUBLE")
        updateFields = ["UBID","BOUNDARY_CONTEXT","MASKEDADMINAREA","WATERAREAKM","MASKEDAREAKM"]
        variables = arcpy.ListFields(estimatesFile,"*DSM")
        for variable in variables:
            name = variable.name
            newField =  name.replace("DSM","CNTM")
            # add the field
            arcpy.AddField_management(memFishnet,newField,"DOUBLE")
            # append the newField to updateFields, and the variable.name to searchFields
            updateFields.append(newField)
            searchFields.append(name)
        # read estimates into memory
        try:
            densities = tableToDict(estimatesFile,searchFields)
        except:
            return "Error in " + iso + ": Creating Estimates Dictionary"
        # write the density estimates to estimatesFile
        try:
            # read the values
            with arcpy.da.UpdateCursor(memFishnet,updateFields) as rows:
                for row in rows:                    
                    # grab the ubid
                    ubid = row[0]
                    if ubid in contexts:
                        row[1] = contexts[ubid][1]
                    else:
                        row[1] = 0
                    waterareakm = row[3]
                    # set the fields
                    pixelarea = row[4]
                    i = 0
                    j = -3
                    for field in updateFields:                        
                        if i < 5:
                            i = i + 1
                            j = j + 1
                            pass
                        else:
                            if not ubid in densities:
                                row[i]= 0
                            else:
                                # assign the admin area
                                row[2] = densities[ubid][1]
                                # calculate the counts
                                row[i]= float(densities[ubid][j]) * float(pixelarea)
                            i = i + 1
                            j = j + 1
                    # update the row
                    rows.updateRow(row)
        except:
            return "Error in " + rootName + ": Writing Updates: " + str(row)
        # finally write the intersect table
        try:
            intersectTable = outGDB + os.sep + rootName + "_intersect_estimates_table"
            arcpy.CopyRows_management(memFishnet,intersectTable)
        except:
            return "Error in " + rootName + ": Writing Table to Disk"
        # compact the file gdb to save space and improve performance
        arcpy.Compact_management(outGDB)
        return "Processed "+ outGDB + " " + str(datetime.datetime.now()-processTime)
    except:
        return "Error while processing " + outGDB + " " + str(datetime.datetime.now()-processTime) + " " + arcpy.GetMessages()
     

def main():
    host = socket.gethostname()
    if host == 'Devsedarc3':
        workspace = r'F:\gpw\release_4_1\process'
    elif host == 'Devsedarc4':
        workspace = r'D:\gpw\release_4_1\process'
    arcpy.env.workspace = workspace
    print "processing"
    procList = arcpy.ListWorkspaces("*")
    print procList
    # must create procList
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
