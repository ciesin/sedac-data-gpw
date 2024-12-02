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

arcpy.env.workspace = workspace

# define parameters list
ingestParameters = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\scratch\dbfs\ingest_fgdbs_8_17_15_5.dbf'

# create search cursor to crawl ingest parameters
isoList = []
with arcpy.da.SearchCursor(ingestParameters,"ISO") as rows:
    for row in rows:
        rowItem = str(row[0])
        isoList.append(rowItem)
print isoList
for iso in isoList:
    print iso
    gdb = workspace + os.sep + iso + ".gdb"
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
        overwriteTables = True
        print inputPopTable
        arcpy.LoadAndValidateTables_landv(iso,inputPopTable,None,
                                          ingestPopLevel,estimateYear,
                                          yearField,inputSexTable,None,
                                          ingestSexLevel,None,None,overwriteTables)
  

