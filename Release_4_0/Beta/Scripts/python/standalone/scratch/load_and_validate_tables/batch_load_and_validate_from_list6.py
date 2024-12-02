# import libraries
import arcpy, os, datetime, sys
sys.path.insert(0, r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions')
from validateSchema import checkForField 

# load custom toolbox
arcpy.ImportToolbox(r'\\Dataserver0\gpw\GPW4\Beta\Scripts\toolboxes\ingest_and_validate_gpw4.tbx')

# set workspace
workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
arcpy.env.workspace = workspace

# define parameters list
ingestParameters = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\ancillary.gdb\ingest_parameters_6'

# create search cursor to crawl ingest parameters
with arcpy.da.SearchCursor(ingestParameters,"*") as rows:
    for row in rows:
        iso = row[1]
        populationTable = row[2]
        populationSheet = row[3]
        populationLevel = int(row[4])
        populationYear = int(row[5])
        yearField = "CENSUS_YEAR"
        sexTable = row[8]
        sexSheet = row[9]
        if row[10]==None:
            sexLevel = None
        else:
            sexLevel = int(row[10])
        lookupTable = row[6]
        lookupSheet = row[7]
        overWrite = True
        try:
            arcpy.LoadAndValidateTables_landv(iso,populationTable,populationSheet,populationLevel,populationYear,
                                              yearField,sexTable,sexSheet,sexLevel,lookupTable,lookupSheet,overWrite)
            print "Validated " + iso
        except:
            print "Validation failed for " + iso
            print arcpy.GetMessages()

        
