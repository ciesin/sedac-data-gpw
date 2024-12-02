# validates the FGDBTs - jsquires 08/03/2015
# rewrote some code from Kytt

# import libraries
import arcpy, os, datetime, sys
sys.path.insert(0, r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions')
from validateSchema import checkForField 

# load custom toolbox
arcpy.ImportToolbox(r'\\Dataserver0\gpw\GPW4\Beta\Scripts\toolboxes\ingest_and_validate_gpw4.tbx','landv')

# set workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\states_variables'

arcpy.env.workspace = workspace

# define parameters list
ingestParameters = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\ancillary.gdb\usa_fgdbs_8_19_15'

# create search cursor to crawl ingest parameters
isoList = ["usa_oh","usa_ok","usa_og"]

#["usa_mt","usa_nc","usa_nd"]#,
##           "usa_ne","usa_nh","usa_nj",
##           "usa_nm","usa_nv","usa_ny",
##           "usa_oh","usa_ok","usa_og",
##           "usa_pa","usa_ri","usa_sc"]

print isoList
for iso in isoList:
    gdb = workspace + os.sep + iso + ".gdb"
    outGDB = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles' + os.sep + iso + ".gdb"
    if arcpy.Exists(outGDB):
        print outGDB + " already exists"
    else:
        arcpy.env.workspace = gdb
        tables = arcpy.ListTables("{}_admin*input_population".format(iso[:6]))
        for tbl in tables:
            print "Processing: {}".format(tbl)
            tblInfo = tbl.split("_")
            inputPopTable = gdb + os.sep + tbl
            ingestPopLevel = tblInfo[2][-1:]
            
            estimateYear = tblInfo[3]
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
            print iso
            print inputPopTable
            print yearField
            print inputSexTable
            arcpy.LoadAndValidateTables_landv(iso,inputPopTable,None,
                                              ingestPopLevel,estimateYear,
                                              yearField,inputSexTable,None,
                                              ingestSexLevel,None,None,overwriteTables)
      


