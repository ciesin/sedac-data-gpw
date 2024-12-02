# Kytt MacManus
# December 2016

# Restructure the input raw country data into variable tables.

# import libraries globally 
import arcpy,datetime,os,sys,multiprocessing
scriptTime = datetime.datetime.now()
# define global variables
rootPath = r'D:\gpw\release_4_1\loading'
gdbRoot = r'D:\gpw\release_4_1\loading\loading_table.gdb'
templateWS = r'D:\gpw\release_4_1\loading\templates.gdb'
arcpy.env.workspace = templateWS
templates = arcpy.ListTables("*template")
templates.remove('gpw4_variable_template')
templates.remove('lookup_template')
templateList = [os.path.join(templateWS,t) for t in templates]
##print templateList

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

def process(gdb):
    try:
        outGDB = gdb


        # note if this is run with the section below active it
        # only works for the highest resolution table
        # with the comment it fills in lower resolution tables
        # shortcut, but no time FIX LATER
        
        # get the estimates table from the last round
        # and grab USCID UBID and AGRID from it...it is just easier
        # than going back to the lookup tables!
        # read estimates into memory
##        try:
##            estimatesGDB = gdb.replace(os.path.dirname(gdb),r'D:\gpw\release_4_1\input_data\pop_tables')
##            arcpy.env.workspace = estimatesGDB
##            estimatesFile = arcpy.ListTables("*estimates")[0]
##            codes = tableToDict(estimatesFile,["USCID","UBID","AGRID"])
##        except:
##            return "Error in " + iso + ": Creating Estimates Dictionary"
        
        processTime = datetime.datetime.now()
        returnList = []
        # grab the raw tables
        arcpy.env.workspace=gdb
        tbls=arcpy.ListTables("*raw")
##        return tbls
        for tbl in tbls:
            # grab values
            tblSplit = os.path.basename(tbl).split("_")
            iso = tblSplit[0]
            adminLevel = tblSplit[1]
            year = tblSplit[2]
            # instantiate lists and dicts
            variableList = []
            tabDict={}
            # define the list of fields in the input table
            fieldLists = arcpy.ListFields(tbl,'A*')
            fields = [f.name for f in fieldLists]
            fieldsUpper = [f.name.upper() for f in fieldLists]
            for template in templateList:
                tblName = iso + "_" + str(adminLevel) + "_" + str(year) + "_" + os.path.basename(template).replace("_template","")
                memTable = 'in_memory' + os.sep + tblName
                outTable = outGDB + os.sep + tblName
                if arcpy.Exists(outTable):
##                    arcpy.Delete_management(outTable)
                    returnList.append(str(str(tblName + " already exists ") + str(datetime.datetime.now()-processTime)))
                    continue
                # define list of search fields
                searchFields = ['USCID']
                searchFieldsUpper = ['USCID']
                # define list of fields present in the template
                templateFieldList = arcpy.ListFields(template,'A*')
                templateFields = [u.name for u in templateFieldList]
                for templateField in templateFields:
                    # if the template field is included in the list of fields in our table
                    if templateField in fieldsUpper:
                        # add the actual (non upper case) field to the searchFields
                        searchFields.append(fields[fieldsUpper.index(templateField)])
                        # also keep track of the upper version of the field name
                        searchFieldsUpper.append(templateField)
                # if no fields from the template were added
                if len(searchFields)==1:
                    returnList.append(str(str(iso + " does not have data on " + os.path.basename(template)) +  str(datetime.datetime.now()-processTime)))
                    continue
                # if a NRBT field is the first field then it doesn't have data
                elif searchFields[1]=='ANRBT' or searchFields[1]=='ANRMT' or searchFields[1]=='ANRFT' or searchFields[1]=='ANRBU'or searchFields[1]=='ANRBR':
                    returnList.append(str(str(iso + " does not have data on " + os.path.basename(template)) + str(datetime.datetime.now()-processTime)))
                    continue
                # if the first field is a PLUS field then there is no data
                elif searchFields[1][4:8]=='PLUS' or searchFields[1][4:8]=='plus':
                    returnList.append(str(str(iso + " does not have data on " + os.path.basename(template)) + str(datetime.datetime.now()-processTime)))
                    continue
                else:
                    # otherwise read the data into the appropriate structure
    ##                if os.path.basename(template).replace("_template","").split("_")[-1]=="singleyear": 
    ##                    return searchFields
                    # read the input table into a dictionary
                    with arcpy.da.SearchCursor(tbl,searchFields) as rows:
                        for row in rows:
                            tabDict[row[0]]=row
                    # create memTable
                    arcpy.CopyRows_management(template,memTable)
                    # insert the data in memTable
                    with arcpy.da.InsertCursor(memTable,searchFieldsUpper) as irows:
                        for key, value in tabDict.iteritems():
                            irows.insertRow(value)
##                    # update the codes
##                    if tblName.split("_")[-1]=='total':
##                        updateFields = ['USCID','UBID','AGRID']
##                    else:
##                        updateFields = ['USCID','UBID']
##                    with arcpy.da.UpdateCursor(memTable,updateFields) as urows:
##                        for urow in urows:
##                            uscid = urow[0]
##                            ubid = codes[uscid][1]
##                            urow[1] = ubid
##                            if tblName.split("_")[-1]=='total':
##                                agrid = codes[uscid][2]
##                                urow[2] = agrid
##                            urows.updateRow(urow)
                            
                    arcpy.CalculateField_management(memTable,"ISO",'"'+iso.upper()+'"',"PYTHON")
                    # copy to disk
                    arcpy.CopyRows_management(memTable,outTable)
                    returnList.append(str("Created " + os.path.basename(outTable)))
            returnList.append(str(str("Processed " + iso) + " " + str(datetime.datetime.now()-processTime)))

    except:
        returnList.append(str(str("Error while processing " + iso) + str(datetime.datetime.now()-processTime)))
    return returnList
def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    # list tables
    gdbs = arcpy.ListWorkspaces("*")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
    pool = multiprocessing.Pool(processes=20, maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        if result == None:
            continue
        for result2 in result:
            print result2
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()

    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()




