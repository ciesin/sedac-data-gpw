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
    inputPopTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\population_gis_tables\estimates.gdb' + os.sep + iso + "_estimates"
    ingestPopTab = None
    ingestPopLevel = table.split("_")[1][-1:]
    estimateYear = table.split("_")[2]
    if len(arcpy.ListFields(table,"*YEAR*"))>0:
        yearField = arcpy.ListFields(table,"*YEAR*")[0].name
    else:
        yearField = "CENSUS_YEAR"
    inputSexTable = None
    ingestSexTab = None
    ingestSexLevel = None
    lookUpTable = None
    lookUpTab = None
    overwriteTables = False

    try:
        arcpy.LoadAndValidateTables(iso,inputPopTable,ingestPopTab,ingestPopLevel,
                                    estimateYear,yearField,inputSexTable,
                                    ingestSexTab,ingestSexLevel,lookUpTable,
                                    lookUpTab,overwriteTables)
        print "Processed " + table
        print datetime.datetime.now() - startTime
    except:
        print table + " processing failed"
