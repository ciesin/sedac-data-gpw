# Kytt MacManus
# 9-30-16

# this script reads the loading table and imports the necessary tables
# tables might originate as excel files, csv files, or gdb tables
# since the structure of the loading summary mixes xls and gdb tables
# we must test to see what we are working with and process accordingly
# agr files are type csv and are passed into their own import function

# import libraries globally and define workspaces
import arcpy,os,datetime
rootPath = r'Q:\gpw\release_4_1\loading'
grWS = rootPath + os.sep + 'growth_rates.gdb'
hlWS = rootPath + os.sep + 'highlevel_census.gdb'
lWS = rootPath + os.sep + 'lowerlevel_census.gdb'
llWS = rootPath + os.sep + 'lowestlevel_census.gdb'
lookupWS = rootPath + os.sep + 'lookup_tables.gdb'
# define loading table
loadingTable = rootPath + os.sep + r'loading_table.gdb\loading_9_27_16'
# define dictionaries
hlCensus={}
hlLookup={}
lCensus={}
llCensus={}
grPath={}
with arcpy.da.SearchCursor(loadingTable,"*") as rows:
    for row in rows:
        # grab ISO
        iso = row[1]
        # populate dictionaries
        hlCensus[iso]=(row[3],row[4])
        hlLookup[iso]=(row[5],row[6])
        lCensus[iso]=(row[7],row[8])
        llCensus[iso]=(row[9],row[10])
        grPath[iso]=row[11]
# function to upload table from csv file
def importFromCSV(dictionary):
    outWS = grWS
    for iso, inTable in dictionary.iteritems():
        if inTable == "Beta gdb":
            continue
        outFile = iso.lower()
        try:
            arcpy.TableToTable_conversion(inTable,outWS,outFile)
            print "Created " + outFile
        except:
            print "Error creating " + outFile + " from " + inTable
# function to copy table from an existing gdb
def copyFromGDB(iso,outWS):
    betaGDB = r'Q:\gpw\pop_tables' + os.sep + iso.lower() + '.gdb'
    if not arcpy.Exists(betaGDB):
        print "###MISSING " + betaGDB
        return
    arcpy.env.workspace = betaGDB
    # grab the data from betaGDB
    inTable = arcpy.ListTables("*total_pop_raw")[0]
    outFile = outWS + os.sep + os.path.basename(inTable).replace("_total_pop_raw","")
    if not arcpy.Exists(outFile):
        try:
            arcpy.CopyRows_management(inTable,outFile)
            print "Created " + outFile
        except:
            print "Error creating " + outFile + " from " + inTable

# function to import excel tables
def importFromExcel(dictionary):
    # determine the appropriate outWS
    if dictionary == hlCensus:
        outWS = hlWS
    elif dictionary == hlLookup:
        outWS = lookupWS
    elif dictionary == lCensus:
        outWS = lWS
    elif dictionary == llCensus:
        outWS = llWS   
    for key, values in dictionary.iteritems():
        iso = key
        xls = values[0]
        tab = values[1]
        # condition to decide whether to use the
        # excel to table tool, or to copy from
        # an existing GDB
        if xls == "Beta gdb":
            copyFromGDB(iso,outWS)
            continue
        # add a second condition to skip the record if it is NA
        elif xls == "NA":
            continue
        # parse the xls tab to determine the
        # name of the outFile
        if outWS == lookupWS:
            outFile = outWS + os.sep + iso.lower() + "_lookup"
        else:
            outFile = outWS + os.sep + iso.lower() + "_" + tab.split("_")[1].lower() + "_" + tab.split("_")[3]
        if not arcpy.Exists(outFile):
            try:
                arcpy.ExcelToTable_conversion(xls,outFile,tab)
                print "Created " + outFile
            except:
                print "Error creating " + outFile + " from " + xls
               
# define a main in order to test and troubleshoot functions
def main():
    scriptTime = datetime.datetime.now()
    excelDictionaries = [hlCensus,hlLookup,lCensus,llCensus]#
    for d in excelDictionaries:
        importFromExcel(d)
    importFromCSV(grPath)                                
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()
