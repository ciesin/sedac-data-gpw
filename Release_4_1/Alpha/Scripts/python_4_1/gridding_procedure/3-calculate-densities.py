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
    iso = os.path.basename(outGDB)[:-4]
    try:
        arcpy.env.workspace = outGDB
        adminBoundaries = arcpy.ListFeatureClasses("*_gridding")[0]
        # define initial list of searchFields
        boundarySearchFields = ["UBID","MASKEDAREAKM"]
        # read boundary area into dictionary
        try:
            areas = tableToDict(adminBoundaries,boundarySearchFields)
        except:
            return "Error in " + iso + ": Creating Areas Dictionary"
        host = socket.gethostname()
        if host == 'Devsedarc3':
            popGDB = r'F:\gpw\release_4_1\input_data\pop_tables' + os.sep + os.path.basename(outGDB)
        elif host == 'Devsedarc4':
            popGDB = r'D:\gpw\release_4_1\input_data\pop_tables' + os.sep + os.path.basename(outGDB)
        arcpy.env.workspace = popGDB
        inPop = arcpy.ListTables("*estimates")
        if len(inPop)==0:
            return inPop + " is missing"
        else:
            estimatesIn = inPop[0]
        # create in memory estimates file
        inMemEstimates = "in_memory" + os.sep + os.path.basename(estimatesIn)
        try:
            arcpy.CopyRows_management(estimatesIn,inMemEstimates)
            arcpy.AddField_management(inMemEstimates,"MASKEDADMINAREA","DOUBLE")
            variables = arcpy.ListFields(inMemEstimates,"E_*") + arcpy.ListFields(inMemEstimates,"UNE_*")
            searchFields = ["UBID","MASKEDADMINAREA"]
            updateFields = ["UBID","MASKEDADMINAREA"]
            for variable in variables:
                newField = variable.name + "_DSM"
                # add the field
                if len(arcpy.ListFields(inMemEstimates,newField))==0:
                    arcpy.AddField_management(inMemEstimates,newField,"DOUBLE")
                # append the newField to updateFields, and the variable.name to searchFields
                updateFields.append(newField)
                searchFields.append(variable.name)
        except:
            return "Error creating " + inMemEstimates
        # read estimates into memory
        try:
            estimates = tableToDict(inMemEstimates,searchFields)
        except:
            return "Error in " + iso + ": Creating Estimates Dictionary"
        # write the density estimates to estimatesFile
        try:
            # read the values
            with arcpy.da.UpdateCursor(inMemEstimates,updateFields) as rows:
                for row in rows:                    
                    # grab the ubid
                    ubid = row[0]
                    if ubid in estimates:
                        # grab the area
                        if ubid in areas:
                            area = areas[ubid][1]
                        else:
                            area = 0
                        # set the fields
                        i = 0
                        for field in updateFields:
                            if i < 1:
                                i = i + 1                            
                            elif i < 2:
                                row[i]=area
                                i = i + 1
                            else:                            
                                # calculate the proportions
                                try:
                                    if ubid in estimates:
                                        row[i]= float(estimates[ubid][i]) / float(area)
                                    else:
                                        row[i]= 0
                                except:
                                    row[i]= 0
                                i = i + 1                            
                    
                    # update the row
                    rows.updateRow(row)
                
        except:
            return "Error in " + iso + ": Writing Updates: " + str(row)
        # write table back to disk
        try:
            estimatesFile = os.path.join(outGDB,os.path.basename(estimatesIn))
            arcpy.CopyRows_management(inMemEstimates,estimatesFile)
        except:
            return "Error writing " + estimatesFile        
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
