# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def evaluate(gdb):
    tables=[]
    processTime = datetime.datetime.now()
    try:
        iso = os.path.basename(gdb)[:-4]
        arcpy.env.workspace = gdb
        singleYearList = arcpy.ListTables("*singleyear")
        # check to see if the iso has single year data
        if len(singleYearList)==0:
            return 0, str(iso + " does not have single year data"), str(datetime.datetime.now()-processTime)
        # grab the table information
        for singleYearTable in singleYearList:
            tableSplit = singleYearTable.split("_")
##            return tableSplit
            admin = tableSplit[1]
            year = tableSplit[2]
            # check to see if there is a group table for that admin level and year
            groupList = arcpy.ListTables(iso+"_"+admin+"_"+year+"*group")
            if len(groupList)>0:
                return 0, str(iso + " already has group data for " + admin + " " + year), str(datetime.datetime.now()-processTime)
            # otherwise return the singleYearTable to be processed
            else:
                tables.append(os.path.join(gdb,singleYearTable))
        return 1, tables, str(datetime.datetime.now()-processTime)
    except:
        return str("Error while processing " + iso), str(datetime.datetime.now()-processTime)
    
def process(tbls):
    arcpy.env.overwriteOutput=True
    returnList = []
    for tbl in tbls:
        processTime = datetime.datetime.now()
        outTable = tbl.replace("singleyear","group")
        try:
            
            # select the correct template to copy into
            tableSplit = os.path.basename(tbl).split("_")
            iso = tableSplit[0]
            admin = tableSplit[1]
            year = tableSplit[2]
            template = r'D:\gpw\release_4_1\loading\templates.gdb' + os.sep + os.path.basename(outTable).replace(iso+"_"+admin+"_"+year+"_","")+"_template"
            # populate the template
            # create a list of fields in the template
            tFlds = arcpy.ListFields(template,"A*")
            templateFields = [tFld.name for tFld in tFlds if len(tFld.name.split("_")) == 2]
            # create a list of fileds in the tbl
            tblFlds = arcpy.ListFields(tbl,"*")
            tblFields = [tblFld.name for tblFld in tblFlds]
            # first interrogate a row of data from the input table
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
            
            # create in memory group tables for calculations
            inMemTable = 'in_memory' + os.sep + os.path.basename(tbl)
            arcpy.CopyRows_management(tbl,inMemTable)
            inMemTemplate = 'in_memory' + os.sep + iso+"_"+admin+"_"+year+"_" + os.path.basename(template).replace("_template","")
            arcpy.CopyRows_management(template,inMemTemplate)

            # cycle through the list of template fields and evaluate whether it will be possible to make the calculation
            # parse the template field name to determine the years to calculate and the variable breakdown (eg FR, MR, MU)
            # for each of the single year variables needed to make the calculation determine if that variable is present
            # in the data by comparing to the dataFields list
            for templateField in templateFields:
                expList = []
                split = templateField.split("_")
                firstYear = split[0][1:]
                lastYear = split[1][0:3]
                suffix = split[1][3:]
                performCalc = 1
                for i in range(int(firstYear),int(lastYear)+1):
                    if len(str(i))==1:
                        vField = "A" + "00" + str(i) + suffix
                    elif len(str(i))==2:
                        vField = "A" + "0" + str(i) + suffix
                    else:
                        vField = "A" + str(i) + suffix
                    # check if vField exists in the tbl
                    if len(arcpy.ListFields(tbl,vField))==0:
                           # then do not perform the calculation
                           performCalc = 0
                           break
                    else:
                        expList.append(vField)
                # if all of the fields are in tbl then performCalc will = 1
                if performCalc == 1:
                    # cycle the expList to create the expression
                    exp = ""
                    for expVar in expList:
                        if len(exp)==0:
                            exp = "!" + expVar + "!"
                        else:
                            exp = exp + " + !" + expVar + "!"
                    # finally perform the calculation
                    arcpy.AddField_management(inMemTable,templateField,"DOUBLE")
                    arcpy.CalculateField_management(inMemTable,templateField,exp,"PYTHON")
                    
            # finally append the in memory tables and write the table to disk
            arcpy.Append_management(inMemTable,inMemTemplate,"NO_TEST")
            arcpy.CopyRows_management(inMemTemplate,outTable)
            returnList.append("Created " + outTable + " " + str(datetime.datetime.now()-processTime))
        except:
            returnList.append("Failed to create " + outTable + " " + str(datetime.datetime.now()-processTime),arcpy.GetMessages())
    return returnList
        

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    gdbs = arcpy.ListWorkspaces("mco*")
    procList=[]                                                                                                                                                                                                     
    # use a pool to evaluate the GDBs
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(evaluate, gdbs)
    for result in results:
        print result
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
        for result3 in result2:
            print result3
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool2.close()
    pool2.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
