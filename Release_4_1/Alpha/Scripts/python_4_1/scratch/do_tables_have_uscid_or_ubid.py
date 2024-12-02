# Kytt MacManus
# December 2016

# import libraries globally 
import arcpy,datetime,os,sys
scriptTime = datetime.datetime.now()
# define global variables
rootPath = r'D:\gpw\release_4_1\loading'
gdbRoot = r'D:\gpw\release_4_1\loading\loading_table.gdb'


templateWS = r'D:\gpw\release_4_1\loading\templates.gdb'
arcpy.env.workspace = templateWS
templates = arcpy.ListTables("*template")
templates.remove('gpw4_variable_template')
templateList = [os.path.join(templateWS,t) for t in templates]
##print templateList


# define census workspaces
hlWS = rootPath + os.sep + 'highlevel_census.gdb'
lWS = rootPath + os.sep + 'lowerlevel_census.gdb'
llWS = rootPath + os.sep + 'lowestlevel_census.gdb'
betaSex = rootPath + os.sep + 'beta_sex_tables.gdb'
# create workspace list
workspaces = [hlWS,lWS,llWS,betaSex]
variableList = []
missingList = []
for workspace in workspaces:
    arcpy.env.workspace = workspace
    # list tables
    tbls = arcpy.ListTables("*")
    tbls.sort()
    for tbl in tbls:
        print tbl
        # grab values
        tblSplit = tbl.split("_")
        iso = tblSplit[0]
        try:
            outGDB = r'D:\gpw\release_4_1\loading\processed' + os.sep + iso + ".gdb"
            if not arcpy.Exists(outGDB):
                arcpy.CreateFileGDB_management(os.path.dirname(outGDB),iso)
                arcpy.CopyRows_management(tbl,os.path.join(outGDB,tbl+"_raw"))
            adminLevel = tblSplit[1]
            year = tblSplit[2]
            tabDict={}
            fieldLists = arcpy.ListFields(tbl,'A*')
            fields = [f.name for f in fieldLists]
            fieldsUpper = [f.name.upper() for f in fieldLists]
            for template in templateList:
##                print os.path.basename(template)
                searchFields = ['USCID']
                searchFieldsUpper = ['USCID']
                templateFieldList = arcpy.ListFields(template,'A*')
                templateFields = [u.name for u in templateFieldList]
                for templateField in templateFields:
                    if templateField in fieldsUpper:
                        searchFields.append(fields[fieldsUpper.index(templateField)])
                        searchFieldsUpper.append(templateField)
                if len(searchFields)==1:
##                        print iso + " does not have data on " + os.path.basename(template)
                        continue
                elif searchFields[1]=='ANRBT':
                    if len(searchFields)==2:
##                        print iso + " does not have data on " + os.path.basename(template)
                        continue
                elif searchFields[1]=='ANRMT':
                    if len(searchFields)==2:
##                        print iso + " does not have data on " + os.path.basename(template)
                        continue
                else:
                    tblName = iso + "_" + str(adminLevel) + "_" + str(year) + "_" + os.path.basename(template).replace("_template","")
                    memTable = 'in_memory' + os.sep + tblName
                    outTable = outGDB + os.sep + tblName
                    if arcpy.Exists(outTable):
                        continue
    ##                print searchFields
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
                    print "Created " + outTable
            print "#############################################################"

        except:
            print "***********************" + iso
        

print "Script Complete in " + str(datetime.datetime.now()-scriptTime)

 




