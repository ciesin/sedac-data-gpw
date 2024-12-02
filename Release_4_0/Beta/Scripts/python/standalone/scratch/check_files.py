import arcpy, os


workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\fishnets_and_clipped_water\rus'

arcpy.env.workspace = workspace

gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

popDictionary = {}

for gdb in gdbs:
    arcpy.env.workspace = gdb
    name = os.path.basename(gdb)[:-4]
    table = arcpy.ListTables("*")[0]
    total = 0
    with arcpy.da.SearchCursor(table,["SUM_E_ATOTPOPBT_2010_CNTM"]) as cursor:
        for row in cursor:
            pop = float(row[0])
            total = total + pop
    popDictionary[name]=total

arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\features\rus\tiles'
gdbList = arcpy.ListWorkspaces("*","FILEGDB")
for fgdb in gdbList:
    arcpy.env.workspace = fgdb
    name = os.path.basename(fgdb)[:-4]
    fc = arcpy.ListFeatureClasses("*")[0]
    total = 0
    with arcpy.da.SearchCursor(fc,["E_ATOTPOPBT_2010"]) as cursor:
        for row in cursor:
            pop = float(row[0])
            total = total + pop
    popDictionary[name]=total

new = sorted(popDictionary)
for n in new:
    print n, popDictionary[n]






        
##        fails= fails + 1
####        print gdb
##        diagList = arcpy.ListTables("*diagnostics*")
##        for diag in diagList:
##            diagnosticsList.append(gdb + os.sep + diag)
##    elif len(arcpy.ListTables("*"))<5:
##        missing = missing + 1
##        print "PRIORITY: " + gdb
##outFile = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\diagnostics.gdb' + os.sep + "diagnostic_summary_8_19_15_2"
##arcpy.Merge_management(diagnosticsList,outFile)
##outFile2 = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\diagnostics.gdb' + os.sep + "problem_countries_8_19_15_2"
##arcpy.Frequency_analysis(outFile,outFile2,"ISO")
##print "This many is missing: {}, and this many failed: {}".format(missing,fails)
##             
             
