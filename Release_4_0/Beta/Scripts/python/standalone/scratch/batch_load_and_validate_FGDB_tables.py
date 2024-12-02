# validates the FGDBTs - jsquires 08/03/2015
# rewrote some code from Kytt

# import libraries
import arcpy, os, datetime, sys
sys.path.insert(0, r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions')
from validateSchema import checkForField 

# load custom toolbox
arcpy.ImportToolbox(r'\\Dataserver0\gpw\GPW4\Beta\Scripts\toolboxes\ingest_and_validate_gpw4.tbx','landv')

# set workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
validated_space = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
arcpy.env.workspace = validated_space

# find the gdbs that have already been processed
processed_gdbs = arcpy.ListWorkspaces('*','FileGDB')

# grab list of gdbs to be validated
arcpy.env.workspace = workspace
gdbs = arcpy.ListWorkspaces("*.gdb", "FileGDB")
gdbs.sort()

for gdb in gdbs:
    print "Looking at {}".format(gdb)
    processed_check = validated_space + os.sep + os.path.basename(gdb)
    # skip gdbs that have already been processed
    if processed_check not in processed_gdbs:
        iso = os.path.basename(gdb).split(".")[0]
        arcpy.env.workspace = gdb
        tables = arcpy.ListTables("{}_admin*input_population".format(iso))
        for tbl in tables:
            print "Processing: {}".format(tbl)
            tblInfo = tbl.split("_")
            inputPopTable = gdb + os.sep + tbl
            ingestPopLevel = tblInfo[1][-1:]
            estimateYear = tblInfo[2]
            if len(arcpy.ListFields(tbl,"*YEAR*"))>0:
                yearField = arcpy.ListFields(tbl,"*YEAR*")[0].name
            else:
                yearField = "CENSUS_YEAR"
            if checkForField(inputPopTable,"ATOTPOPMT"):
                inputSexTable = inputPopTable
                ingestSexLevel = ingestPopLevel
            else:
                inputSexTable = None
                ingestSexLevel = None
            overwriteTables = False
            print inputPopTable
            arcpy.LoadAndValidateTables_landv(iso,inputPopTable,None,ingestPopLevel,estimateYear,yearField,inputSexTable,None,ingestSexLevel,None,None,overwriteTables)
    else:
        print "{} already processed".format(gdb)

