# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
arcpy.env.overwriteOutput=True
def evaluate(gdb):
    tables=[]
    processTime = datetime.datetime.now()
    try:
        iso = os.path.basename(gdb)[:-4]
        arcpy.env.workspace = gdb
        groupList = arcpy.ListTables("*group")
        # check to see if the iso has group data
        if len(groupList)==0:
            return 0, str(iso + " does not have single year data"), str(datetime.datetime.now()-processTime)
        # grab the table information
        for groupTable in groupList:
            tableSplit = groupTable.split("_")
##            return tableSplit
            admin = tableSplit[1]
            year = tableSplit[2]
            # return the groupTable to be processed
            tables.append(os.path.join(gdb,groupTable))
        return 1, tables, str(datetime.datetime.now()-processTime)
    except:
        return str("Error while processing " + iso), str(datetime.datetime.now()-processTime)
    
def process(tbls):
    returnList = []
    for tbl in tbls:
        outTable=tbl
        processTime = datetime.datetime.now()
        try:
            # select the correct template to copy into
            tableSplit = os.path.basename(tbl).split("_")
            iso = tableSplit[0]
            admin = tableSplit[1]
            year = tableSplit[2]
            # create a list of fields in the tbl
            tblFlds = arcpy.ListFields(tbl,"*")
            tblFields = [tblFld.name for tblFld in tblFlds]
            # also create a list of PLUS fields in the tbl
            plusFlds = arcpy.ListFields(tbl,"*PLUS*")
            plusFields = [plusFld.name for plusFld in plusFlds]
            # interrogate a row of data from the input table
            # create a dictionary where key = field name from input table
            # and value = the data from the first row in the table
            rowDict = {}
            # iterate rowDict to determine which fields have data
            with arcpy.da.SearchCursor(tbl,"*") as rows:
                for row in rows:
                    counter = 0
                    for datapoint in row:
                        if datapoint == None:
                            counter+=1
                            continue
                        else:
                            index = tblFields[counter]
                            if index == "ISO" or index == "USCID" or index == "OBJECTID" or index == "AGRID" or index == "UBID":
                                counter+=1
                                continue
                            rowDict[index]=datapoint
                            counter+=1
                    break        
            dataFields = rowDict.keys()
            dataFields.sort()
            
            # determine the highest age in the table
            # first check for a PLUS fields
            calcFields = []
            highestAgeField = dataFields[-1]
            
            if highestAgeField[0:2]=='AN':
                highestAgeField = dataFields[-2]
            if highestAgeField[0:2]=='AN':
                highestAgeField = dataFields[-3]
            if highestAgeField[0:2]=='AN':
                highestAgeField = dataFields[-4]
            if highestAgeField[0:2]=='AN':
                highestAgeField = dataFields[-5]
            if highestAgeField[0:2]=='AN':
                highestAgeField = dataFields[-6]
            if highestAgeField in plusFields:
                highestAge = int(highestAgeField[1:4])
            # if the highest age is not a PLUS field then
            # we need to determine what it is
            else:
                highestAge = int(highestAgeField[5:8])
            
            # determine which plus fields need to be calculated
            for plusField in plusFields:
                    if int(plusField[1:4])<highestAge:
                        calcFields.append(plusField)    
            
            # create in memory group tables for calculations
            inMemTable = 'in_memory' + os.sep + os.path.basename(tbl)
            arcpy.CopyRows_management(tbl,inMemTable)

            # perform the calculations
            for calcField in calcFields:
                suffix = calcField[-2:]
                exp = ""
                # generate the expression
                highestAge = int(calcField[1:4])
                # cycle the data fields
                for dataField in dataFields:
                    if dataField[0:2]=='AN':
                        continue
                    elif not suffix == dataField[-2:]:
                        continue
                    if dataField in plusFields:
                        dataAge = int(dataField[1:4])
                    else:
                        dataAge = int(dataField[5:8])
                    
                    if dataAge > highestAge:
                        if len(exp)==0:
                            exp = "!" + dataField + "!"
                        else:
                            exp = exp + " + !" + dataField + "!"
                if len(exp)==0:
                    continue
                else:
                    # complete the calculation
                    try:
                        arcpy.CalculateField_management(inMemTable,calcField,exp,"PYTHON")
                    except:
                        return arcpy.GetMessages()       
            # finally write the table to disk
            try:
                arcpy.CopyRows_management(inMemTable,outTable)
            except:
                return arcpy.GetMessages()
            returnList.append("Created " + outTable + " " + str(datetime.datetime.now()-processTime))
        except:
            returnList.append("Failed to create " + outTable + " " + str(datetime.datetime.now()-processTime))
    return returnList
        

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    gdbs = arcpy.ListWorkspaces("usaaz*")
    procList = []
    # use a pool to evaluate the GDBs
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(evaluate, gdbs)
    for result in results:
##        print result
        if result[0]==0:
            continue
        # add the list of tables to the processList
        tbls = result[1]
        procList.append(tbls)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
##    process(tbls)
    pool2 = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results2 = pool2.map(process, procList)
    for result2 in results2:
##        print result2
        for result3 in result2:
            print result3
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool2.close()
    pool2.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
