#identify which countries have type double for the pop count fields in the raw table
#    - these have been wrongly converted to type long in the input tables.

# Does NOT look at USA

import os, csv, arcpy
from arcpy import env

env.overwriteOutput = True

output = r'C:\Users\jmills\Desktop\countries_with_decimals.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("ISO","ATOTPOPBT_type","ATOTPOPBT_decimals","ATOTPOPMT_type","ATOTPOPMT_decimals","ATOTPOPFT_type",
                  "ATOTPOPFT_decimals","A_fields_of_type_double","number_of_decimals_in_those_fields"))


# List workspaces
workspace = r'\\Dataserver0\gpw\GPW4\Release_4_0\Beta\Gridding\country\pop_tables'
env.workspace = workspace

# List gdb in workspace
gdbs = arcpy.ListWorkspaces("*","FileGDB")
gdbs.sort()

for gdb in gdbs:
    iso = os.path.basename(gdb)[:-4]
    print iso
    arcpy.env.workspace = gdb

    tpopType = None
    tpopDouble = 0
    mpopType = None
    mpopDouble = 0
    fpopType = None
    fpopDouble = 0
    apopType = 0
    apopDouble = 0

# Select Total Pop raw table
    tpopList = arcpy.ListTables("*total_pop_raw")
    if len(tpopList) != 1:
        print "\tHas more than one total pop raw table"
    else:
        tpop = tpopList[0]

        # Is ATOTPOPBT type double?
        tpopField = arcpy.ListFields(tpop,"ATOTPOPBT")
        tpopType = tpopField[0].type

        if tpopType == "Double":
            with arcpy.da.SearchCursor(tpop,["ATOTPOPBT"]) as cursor:
                for row in cursor:
                    if int(row[0]) != row[0]:
                        tpopDouble = tpopDouble + 1

# Select Sex raw table
    if iso == 'vcs':
        pass
    else:
        spopList = arcpy.ListTables("*sex_variables_raw")
        if len(spopList) != 1:
            print "\tHas more than one sex raw table"
        else:
            spop = spopList[0]

            # Is ATOTPOPFT double?
            fpopField = arcpy.ListFields(spop,"ATOTPOPFT")
            fpopType = fpopField[0].type
            
            if fpopType == "Double":
                with arcpy.da.SearchCursor(spop,["ATOTPOPFT"]) as cursor:
                    for row in cursor:
                        if int(row[0]) != row[0]:
                            fpopDouble = fpopDouble + 1

            # Is ATOTPOPMT double?
            mpopField = arcpy.ListFields(spop,"ATOTPOPMT")
            mpopType = mpopField[0].type
            
            if mpopType == "Double":
                with arcpy.da.SearchCursor(spop,["ATOTPOPMT"]) as cursor:
                    for row in cursor:
                        if int(row[0]) != row[0]:
                            mpopDouble = mpopDouble + 1

            # Count how many A fields are double
            aFieldList = [f.name for f in arcpy.ListFields(spop,"A*","Double")]
            varsFields = []
            for aF in aFieldList:
                if aF == "ATOTPOPBT":
                    pass
                elif aF == "ATOTPOPMT":
                    pass
                elif aF == "ATOTPOPFT":
                    pass
                else:
                    varsFields.append(aF)
            apopType = len(varsFields)
            if len(varsFields) > 1:
                for vF in varsFields:
                    with arcpy.da.SearchCursor(spop,[vF]) as cursor:
                        for row in cursor:
                            if int(row[0]) != row[0]:
                                apopDouble = apopDouble + 1
            elif len(varsFields) == 1:
                with arcpy.da.SearchCursor(spop,[varsFields[0]]) as cursor:
                    for row in cursor:
                        if int(row[0]) != row[0]:
                            apopDouble = apopDouble + 1

            csvFile.writerow((iso,tpopType,tpopDouble,mpopType,mpopDouble,fpopType,fpopDouble,apopType,apopDouble))
    print "finished",iso

print "Done"

