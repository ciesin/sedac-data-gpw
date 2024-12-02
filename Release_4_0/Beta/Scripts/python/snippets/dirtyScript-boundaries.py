# quick dirty script to copy data from alpha gdbs
# not sure if some of the code will be reusable
# retain .py just in case
# sorry for the dirtyness!

import arcpy, os
arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\country_boundaries.gdb'

outGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\country_boundaries_hi_res.gdb'


fcs = arcpy.ListFeatureClasses("*2010")
fcs.sort(reverse=False)
# Create a fieldinfo object
fieldInfo = arcpy.FieldInfo()
fieldInfo.addField("UBID","UBID","VISIBLE","NONE")
for fc in fcs:
    newFC = outGDB + os.sep + fc
##    fl = fc + "_lyr"
##    if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(fc, fl,' "BOUNDARY_CONTEXT" IS NOT NULL'))[0])>0:
##        print fc
    
    arcpy.CopyFeatures_management(fc,newFC)
    print "Created " + newFC
    fields = arcpy.ListFields(newFC,"*")
    fields.remove(fields[0])
    fields.remove(fields[0])
    delFields = []
    for field in fields:
        if field.name=="UBID":
            pass
        elif field.name=="BOUNDARY_CONTEXT":
            pass
        elif field.name=="SHAPE_Length":
            pass
        elif field.name=="SHAPE_Area":
            pass
        else:
            delFields.append(field.name)
    arcpy.DeleteField_management(newFC,delFields)
    print "Deleted " + str(delFields)

















##outGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\population_gis_tables\unchanged_from_alpha.gdb'
##lookupTable = outGDB + os.sep + 'gpw_from_alpha_fgdb'

##with arcpy.da.SearchCursor(lookupTable,"ISO") as searchCursor:
##    for row in searchCursor:
##        iso = row[0].lower()
##        print iso
##        betaGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs' + os.sep + iso + ".gdb"
##        if not arcpy.Exists(betaGDB):
##            print betaGDB
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
