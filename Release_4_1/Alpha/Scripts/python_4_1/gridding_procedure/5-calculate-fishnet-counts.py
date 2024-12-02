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
    processTime = datetime.datetime.now()
    iso = os.path.basename(outGDB)[:3]
    rootName = os.path.basename(outGDB)[:-4]
    try:
        arcpy.env.workspace = outGDB
        # grab intersectTable
        tbls = arcpy.ListTables("*_table")
        if len(tbls)==0:
            return outGDB + " intersect estimates file is missing"
        intersectTable = tbls[0]
        fishnets = arcpy.ListFeatureClasses("*fishnet")
        if len(fishnets)==0:
            return outGDB + " fishnet is missing"
        fishnet = fishnets[0]
        finalFishnet = fishnet + "_processed"
        if arcpy.Exists(finalFishnet):
            arcpy.Delete_management(finalFishnet)
        # create list of fields to generate statistics for
        statsFields = [["PIXELAREA","MAX"],["BOUNDARY_CONTEXT","MAX"],["MASKEDADMINAREA","MEAN"],
                       ["AREAKM","SUM"],["WATERAREAKM","SUM"],["MASKEDAREAKM","SUM"]]
        # list CNTM fields in order to be flexible to whatever variables
        # are present in the country
        cntFields = arcpy.ListFields(intersectTable,"*CNTM")
        if len(cntFields)>0:
            [statsFields.append([field.name,"SUM"]) for field in cntFields]
        # create a summary table in memory
        memSumTbl = 'in_memory' + os.sep + os.path.basename(intersectTable) + "_summary"
        try:
            arcpy.Statistics_analysis(intersectTable,memSumTbl,statsFields,"PIXELID")
        except:
            return "Error in " + rootName + " : making table views " + str(arcpy.GetMessages())
        # read the fishnet into memory
        memFishnet = 'in_memory' + os.sep + os.path.basename(fishnet) + "_view"
        try:
            arcpy.CopyFeatures_management(fishnet,memFishnet)
        except:
            return "Error in " + rootName + " : making fishnet in memory"
        # define initial list of searchFields
        searchFields = ["PIXELID","MAX_PIXELAREA"]
        updateFields = ["PIXELID","PIXELAREA"]
        # create list of variables
        variables = arcpy.ListFields(memSumTbl,"*")
        for variable in variables:
            name = variable.name
            if name == "OBJECTID":
                continue
            elif name == "PIXELID":
                continue
            elif name == "MAX_PIXELAREA":
                continue
            elif name == "FREQUENCY":
                newField = "NUMINPUTS"
            elif name == "MAX_BOUNDARY_CONTEXT":
                newField = "CONTEXT"
            elif name == "MEAN_MASKEDADMINAREA":
                newField = "MEAN_MASKEDADMINAREA"
            else:
                newField =  name.replace("SUM_","")
            # add the field
            arcpy.AddField_management(memFishnet,newField,"FLOAT")
            # append the newField to updateFields, and the variable.name to searchFields
            updateFields.append(newField)
            searchFields.append(name)
##        return (searchFields, updateFields)
        # create dictionary to hold source counts
        try:
            counts = tableToDict(memSumTbl,searchFields)
        except:
            return "Error in " + iso + ": Creating Counts Dictionary"
        # write the estimates to the memFishnet
        try:
            # read the values
            with arcpy.da.UpdateCursor(memFishnet,updateFields) as rows:
                for row in rows:
                    # grab the pixelid
                    pixelid = row[0]
                    if pixelid not in counts:
                        continue
                    # grab the pixelarea
                    pixelarea = row[1]
                    # set the fields
                    i = 0
                    for field in updateFields:                        
                        if i < 2:
                            i = i + 1                            
                            pass
                        # special condition for context row
                        elif i == 3:
                            if counts[pixelid][12]>0:
                                row[i]= 0
                            else:
                                row[i]= counts[pixelid][i]
                            i = i + 1
                        # special condition for areakm
                        elif i == 5:
                            if counts[pixelid][i]<pixelarea:
                                row[i]= counts[pixelid][i]
                            else:
                                row[i]= pixelarea
                            i = i + 1
                        # special condition for waterareakm
                        elif i == 6:
                            if counts[pixelid][i]<pixelarea:
                                row[i]= counts[pixelid][i]
                            else:
                                row[i]= pixelarea
                            i = i + 1
                        # special condition for maskedareakm
                        elif i == 7:
                            if counts[pixelid][i]<pixelarea:
                                row[i]= counts[pixelid][i]
                            else:
                                row[i]= pixelarea
                            i = i + 1
                        else:
                            # calculate the counts
                            row[i]= counts[pixelid][i]
                            i = i + 1
                    # update the row
                    rows.updateRow(row)           
        except:
            return "Error in " + rootName + ": Writing Updates"
        # finally write the final fishnet
        try:
            arcpy.CopyFeatures_management(memFishnet,finalFishnet)
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
