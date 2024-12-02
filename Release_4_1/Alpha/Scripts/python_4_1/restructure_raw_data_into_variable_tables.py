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

def process(tbl):
    processTime = datetime.datetime.now()
    returnList = []
    variableList = []
    # grab values
    tblSplit = os.path.basename(tbl).split("_")
    iso = tblSplit[0]
    try:
        outGDB = r'D:\gpw\release_4_1\loading\processed' + os.sep + iso + ".gdb"
##        # if the gdb exists then it is already processed and can be skipped
##        if arcpy.Exists(outGDB):
##            returnList.append(str(str(iso + " is already processed ") + str(datetime.datetime.now()-processTime)))
##            return returnList
        if not arcpy.Exists(outGDB):
            arcpy.CreateFileGDB_management(os.path.dirname(outGDB),iso)
        rawTable = os.path.basename(tbl)+"_raw"
        if not arcpy.Exists(rawTable):
            arcpy.CopyRows_management(tbl,os.path.join(outGDB,rawTable))
        adminLevel = tblSplit[1]
        year = tblSplit[2]
        tabDict={}
        fieldLists = arcpy.ListFields(tbl,'A*')
        # define the list of fields in the input table
        fields = [f.name for f in fieldLists]
        fieldsUpper = [f.name.upper() for f in fieldLists]
        for template in templateList:
            tblName = iso + "_" + str(adminLevel) + "_" + str(year) + "_" + os.path.basename(template).replace("_template","")
            memTable = 'in_memory' + os.sep + tblName
            outTable = outGDB + os.sep + tblName
            if arcpy.Exists(outTable):
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
                # update the data in memTable
                with arcpy.da.InsertCursor(memTable,searchFieldsUpper) as irows:
                    for key, value in tabDict.iteritems():
                        irows.insertRow(value)
                arcpy.CalculateField_management(memTable,"ISO",'"'+iso.upper()+'"',"PYTHON")
                # copy to disk
                arcpy.CopyRows_management(memTable,outTable)
                returnList.append(str("Created " + os.path.basename(outTable)))
        returnList.append(str(str("Processed " + iso) + " " + str(datetime.datetime.now()-processTime)))

    except:
        returnList.append(str(str("Error while processing " + iso) + str(datetime.datetime.now()-processTime)))
    return returnList
def main():
    # define census workspaces
    hlWS = rootPath + os.sep + 'highlevel_census.gdb'
    lWS = rootPath + os.sep + 'lowerlevel_census.gdb'
    llWS = rootPath + os.sep + 'lowestlevel_census.gdb'
    betaSex = rootPath + os.sep + 'beta_sex_tables.gdb'
    usWS = rootPath + os.sep + 'us_high_resolution.gdb'
    # create workspace list
    
    workspaces = [usWS]#[hlWS,lWS,llWS,betaSex]#
    for workspace in workspaces:
        print workspace
        tblList = []
        arcpy.env.workspace = workspace
        # list tables
        tbls = arcpy.ListTables("*")
        # add the tables to the tblList
        for tbl in tbls:
            table = os.path.join(workspace,tbl)
            tblList.append(table)
##    tblList.sort()
##    for t in tblList:
##        print t
        pool = multiprocessing.Pool(processes=2,maxtasksperchild=1)
        results = pool.map(process, tblList)
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




