# Kytt MacManus
# 9-30-16

# this script reads the loading table and imports the necessary tables
# tables might originate as excel files, csv files, or gdb tables
# since the structure of the loading summary mixes xls and gdb tables
# we must test to see what we are working with and process accordingly
# agr files are type csv and are passed into their own import function
##THIS SCRIPT IS EXECUTED ON DEVSEDARC4
# import libraries globally and define workspaces
import arcpy,os,datetime
rootPath = r'D:\gpw\release_4_1\loading'
grWS = rootPath + os.sep + 'growth_rates.gdb'
hlWS = rootPath + os.sep + 'highlevel_census.gdb'
lWS = rootPath + os.sep + 'lowerlevel_census.gdb'
llWS = rootPath + os.sep + 'lowestlevel_census.gdb'
lookupWS = rootPath + os.sep + 'lookup_tables.gdb'
# define loading table
loadingTable = rootPath + os.sep + r'loading_table.gdb\loading_12_16_16'
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
            betaGDB = r'D:\gpw\4_0_prod\pop_tables' + os.sep + iso.lower() + '.gdb'
            if not arcpy.Exists(betaGDB):
                print "###MISSING " + betaGDB
                continue
            arcpy.env.workspace = betaGDB
            # grab the data from betaGDB
            inTable = arcpy.ListTables("*growth_rate*")[0]
            outFile = os.path.basename(inTable)
        else:
            try:
                with arcpy.da.SearchCursor(inTable,["gr_start_year","gr_end_year","gr_level"]) as rows:
                    for row in rows:
                        startYear=row[0]
                        endYear=row[1]
                        grLevel=row[2]
                        break
                outFile = iso.lower()+"_growth_rate_admin"+str(grLevel)+"_"+str(startYear)+"_"+str(endYear)
            except:
                print "Check: " + inTable
                return
        if not arcpy.Exists(outWS + os.sep + outFile):
            try:
                arcpy.TableToTable_conversion(inTable,outWS,outFile)
                print "Created " + outFile
            except:
                print "Error creating " + outFile + " from " + inTable
# function to copy table from an existing gdb
def copyFromGDB(iso,outWS):
    print iso
    betaGDB = r'D:\gpw\4_0_prod\pop_tables' + os.sep + iso.lower() + '.gdb'
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
    try:
        sexTable = arcpy.ListTables("*sex_variables_raw")[0]
    except:
        return
    sexFile = r'D:\gpw\release_4_1\loading\beta_sex_tables.gdb' + os.sep + os.path.basename(sexTable).replace("_sex_variables_raw","")
    if os.path.basename(outFile).split("_")[1]<>os.path.basename(sexFile).split("_")[1]:
        if not arcpy.Exists(sexFile):
            try:
                arcpy.CopyRows_management(sexTable,sexFile)
                print "Created " + sexFile
            except:
                print "Error creating " + sexFile + " from " + sexTable
##    else:
##        print sexFile

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
##        else:
##            continue
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
        else:
            print outFile
               
# define a main in order to test and troubleshoot functions
def main():
    scriptTime = datetime.datetime.now()
    excelDictionaries = [hlCensus,hlLookup,lCensus,llCensus]#
##    for d in excelDictionaries:
####        for key, value in d.iteritems():
####            print key,value
##        importFromExcel(d)
    importFromCSV(grPath)                                
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()
