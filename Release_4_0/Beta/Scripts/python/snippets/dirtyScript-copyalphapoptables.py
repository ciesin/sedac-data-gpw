# quick dirty script to copy data from alpha gdbs
# not sure if some of the code will be reusable
# retain .py just in case
# sorry for the dirtyness!

import arcpy, os
outGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\population_gis_tables\unchanged_from_alpha.gdb'
lookupTable = outGDB + os.sep + 'gpw_from_alpha_fgdb'

with arcpy.da.SearchCursor(lookupTable,"ISO") as searchCursor:
    for row in searchCursor:
        iso = row[0].lower()
        print iso
        betaGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs' + os.sep + iso + ".gdb"
        if not arcpy.Exists(betaGDB):
            print betaGDB
##        if iso == "usa":
##            continue
##        else:
##            popGDB = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs' + os.sep + iso + ".gdb"
##            arcpy.env.workspace = popGDB
##            
##            estimateGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\population_gis_tables\estimates.gdb'
##            if len(arcpy.ListTables(iso + "_estimates"))>0:
##                estimateTable = arcpy.ListTables(iso + "_estimates")[0]
##                outEstimateTable = estimateGDB + os.sep + os.path.basename(estimateTable) 
##                if not arcpy.Exists(outEstimateTable):
##                    print outEstimateTable
####                    try:
####                        arcpy.CopyRows_management(estimateTable,outEstimateTable)
####                        print "Copied " + estimateTable
####                    except:
####                        print arcpy.GetMessages()
##
##            outPopGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\population_gis_tables\pop.gdb'
##            if len(arcpy.ListTables(iso + "*_input_population"))>0:
##                popTable = arcpy.ListTables(iso + "*_input_population")[0]
##                outPopTable = outPopGDB + os.sep + os.path.basename(popTable)
##                if not arcpy.Exists(outPopTable):
##                    print outPopTable
####                    try:
####                        arcpy.CopyRows_management(popTable,outPopTable)
####                        print "Copied " + popTable
####                    except:
####                        print arcpy.GetMessages()
