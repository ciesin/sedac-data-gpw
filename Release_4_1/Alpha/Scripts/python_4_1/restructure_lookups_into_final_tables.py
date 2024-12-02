# Ingest and Intergrate Lookup Tables
# Kytt MacManus
# 1-9-2017

# need to also know which tables do not have fields so use the full set for evaluation
import arcpy, os, datetime, multiprocessing
scriptTime = datetime.datetime.now()


def process(iso):
    processTime = datetime.datetime.now()
    returnList = []
    try:
        outGDB = r'D:\gpw\release_4_1\loading\processed' + os.sep + iso + ".gdb"
        lookupGDB = r'D:\gpw\release_4_1\loading\lookup_tables.gdb'
        searchTable = None
        # specify the tables
        arcpy.env.workspace = lookupGDB
        try:
            lookupTable = os.path.join(lookupGDB,arcpy.ListTables(iso+"*")[0])
        except:
            try:
                arcpy.env.workspace = outGDB
                lookupTable = os.path.join(outGDB,arcpy.ListTables("*raw")[0])
            except:
                returnList.append(iso + " does not have a lookup table. Must investigate")
                
##        return [lookupTable]
        # define the list of fields in the lookup table
        lookupFieldLists = arcpy.ListFields(lookupTable,'*')
        lookupFields = [f.name for f in lookupFieldLists if f.name<>"OBJECTID"]
        lookupFieldsUpper = [f.name.upper() for f in lookupFieldLists if f.name<>"OBJECTID"]
        # create list to hold the seach fields
        lookupSearch = []

        # define list of fields present in the template
        templateTable = r'D:\gpw\release_4_1\loading\templates.gdb\lookup_template'
        templateFieldList = arcpy.ListFields(templateTable,'*')
        templateFields = [u.name for u in templateFieldList if u.name<>"OBJECTID"]

        # grab the raw table
        arcpy.env.workspace = outGDB
        tbls = arcpy.ListTables("*raw")
        rawTbl = tbls[0]
         # define the output table
        tblSplit = rawTbl.split("_")    
        adminLevel = tblSplit[1]                
        year = tblSplit[2]
##        return [lookupTable, rawTbl]
        # define and check for the output table
        tblName = iso+"_"+adminLevel+"_"+year+"_lookup"
        memTable = 'in_memory' + os.sep + tblName
        outTable = os.path.join(outGDB,tblName)
        if arcpy.Exists(outTable):
            returnList.append(outTable + " already exists")
            return returnList
                              
        # define the list of fields in the raw table
        rawLists = arcpy.ListFields(rawTbl,'*')
        rawFields = [f.name for f in rawLists if f.name<>"OBJECTID"]
        rawFieldsUpper = [f.name.upper() for f in rawLists if f.name<>"OBJECTID"]
        # create list to hold the seach fields
        rawSearch = []
        
                          
        # the fields which are needed to populate outTable are those
        # which are included in the templateFields                
        for templateField in templateFields:
            # evaluate if the field is in the lookupFields
            if templateField in lookupFieldsUpper:
                # if so append it to lookupSearch
                lookupSearch.append(lookupFields[lookupFieldsUpper.index(templateField)])
            # evaluate if the field is in the rawFields
            if templateField in rawFieldsUpper:
                # if so append it to lookupSearch
                rawSearch.append(rawFields[rawFieldsUpper.index(templateField)])
        
        # check if rawSearch contains UBID
        if 'UBID' in rawSearch:
            # check that it is not null
            with arcpy.da.SearchCursor(rawTbl,("UBID")) as cS:
                for cR in cS:
                    if cR[0] <> None:
                        # then rawSearch must be primary to avoid
                        # the juxtaposition of data
                        searchFields = rawSearch
                        searchTable = rawTbl
                        break
        # if not, then the lookup Table must be primary
        elif 'UBID' in lookupSearch:
            searchFields = lookupSearch
            searchTable = lookupTable
        # if UBID is in neither log an error
        else:
            returnList.append(iso + " is missing a UBID " + str(datetime.datetime.now()-processTime)) 
        
        # if searchTable is not null read it into a dictionary
        valueDict = {}
        try:
            if searchTable <> None:
                with arcpy.da.SearchCursor(searchTable,searchFields) as sS:
                    for sR in sS:
                        if sR[searchFields.index("USCID")] == None:
                            continue
                        elif sR[searchFields.index("USCID")] == "":
                            continue
                        valueDict[sR[searchFields.index("USCID")]]=sR
                        
        except:
            returnList.append(iso + " problem reading valueDict")
            return returnList
##        return [valueDict.keys()]
        # finally write the data to outTable
        # create the mem table
        arcpy.CopyRows_management(templateTable,memTable)
        # update the data in memTable
        with arcpy.da.InsertCursor(memTable,searchFields) as irows:
            for key, value in valueDict.iteritems():
                irows.insertRow(value)
        arcpy.CalculateField_management(memTable,"ISO",'"'+iso.upper()+'"',"PYTHON")
        arcpy.CalculateField_management(memTable,"CENSUS_YEAR",'"'+str(year)+'"',"PYTHON")
        # copy to disk
        arcpy.CopyRows_management(memTable,outTable)
        returnList.append(str("Processed " + iso + " " + str(datetime.datetime.now()-processTime)))

    except:
        returnList.append(str("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime) + " " + str(arcpy.GetMessages())))
    
    return returnList
def main():
    arcpy.env.workspace = r'D:\gpw\release_4_1\loading\processed'
    gdbs = arcpy.ListWorkspaces("bra*")+arcpy.ListWorkspaces("btn*")+arcpy.ListWorkspaces("can*")+arcpy.ListWorkspaces("cod*")+arcpy.ListWorkspaces("esh*")+arcpy.ListWorkspaces("flk*")+arcpy.ListWorkspaces("ggy*")+arcpy.ListWorkspaces("ind*")+arcpy.ListWorkspaces("irq*")+arcpy.ListWorkspaces("mex*")+arcpy.ListWorkspaces("mus*")+arcpy.ListWorkspaces("nzl*")+arcpy.ListWorkspaces("phl*")+arcpy.ListWorkspaces("svk*")+arcpy.ListWorkspaces("ury*")+arcpy.ListWorkspaces("vcs*")
    isos = [os.path.basename(gdb)[:-4] for gdb in gdbs]
    isos.sort()

    # use a pool to evaluate the GDBs
    pool = multiprocessing.Pool(processes=16,maxtasksperchild=1)
    results = pool.map(process, isos)
    for result in results:
        for result2 in result:
            print result2
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
## 
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
