# execute load and validate tables in a batch
# written to test against the "unchanged alpha tables"
# 6-30-15
# Kytt MacManus

# import libraries
import arcpy, os, datetime
# load custom toolbox
arcpy.ImportToolbox(r'\\Dataserver0\gpw\GPW4\Beta\Scripts\toolboxes\ingest_and_validate_gpw4.tbx')

# declare input GDB as arcpy.env.workspace
workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\population_gis_tables\pop.gdb'
arcpy.env.workspace = workspace
# list input pop tables
tables = arcpy.ListTables("*population")
# iterate
for table in tables:
    startTime = datetime.datetime.now()
    print "Considering " + table
    # parse parameters for load tool
    iso = table.split("_")[0].lower()
    inputTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\population_gis_tables\estimates.gdb' + os.sep + iso + "_estimates"
    excelTab = None
    adminLevel = table.split("_")[1][-1:]
    estimateYear = table.split("_")[2]
    if len(arcpy.ListFields(table,"*YEAR*"))>0:
        yearField = arcpy.ListFields(table,"*YEAR*")[0].name
    else:
        yearField = "CENSUS_YEAR"
    lookupTable = None
    diagnosticTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'+ os.sep + iso + '.gdb' + os.sep + iso + '_admin' + adminLevel + '_' + estimateYear + "_ingest_diagnostics"
    # if diagnostic table exists, then delete the FGDB
    if arcpy.Exists(diagnosticTable):
        print "Processing " + iso
        arcpy.Delete_management(r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'+ os.sep + iso + '.gdb')
        try:
            arcpy.LoadInputPopulation(iso,inputTable,excelTab,adminLevel,estimateYear,yearField,lookupTable)
            print "Processed " + table
            print datetime.datetime.now() - startTime
        except:
            print table + " processing failed"
    else:
        pass
