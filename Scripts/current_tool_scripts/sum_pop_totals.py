# Jane Mills
# September 1, 2014

# adapted from Erin's version of Kytt's count_input_units.py script

# NOTE: how does this script handle -9999?????

# Import Libraries
import arcpy, os, csv

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'


# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
# Will have to go back and get data for the countries that are in folders (bra, can, grl, rus, usa)
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# define csv file
attributes =r'C:\Users\jmills\Downloads\sum_pop_counts.csv'

# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))

csvFile.writerow(["COUNTRYCODE","CENSUSYEAR","ATOTPOPBT","estimates_E_ATOTPOPBT_2000","estimates_E_ATOTPOPBT_2005",
                  "estimates_E_ATOTPOPBT_2010","estimates_E_ATOTPOPBT_2015","estimates_E_ATOTPOPBT_2020",
                  "estimates_UNE_ATOTPOPBT_2000","estimates_UNE_ATOTPOPBT_2005","estimates_UNE_ATOTPOPBT_2010",
                  "estimates_UNE_ATOTPOPBT_2015","estimates_UNE_ATOTPOPBT_2020",
                  "boundary_E_ATOTPOPBT_2000","boundary_E_ATOTPOPBT_2005","boundary_E_ATOTPOPBT_2010",
                  "boundary_E_ATOTPOPBT_2015","boundary_E_ATOTPOPBT_2020","boundary_UNE_ATOTPOPBT_2000",
                  "boundary_UNE_ATOTPOPBT_2005","boundary_UNE_ATOTPOPBT_2010","boundary_UNE_ATOTPOPBT_2015",
                  "boundary_UNE_ATOTPOPBT_2020",
                  "fishnet_E_ATOTPOPBT_2000","fishnet_E_ATOTPOPBT_2005","fishnet_E_ATOTPOPBT_2010",
                  "fishnet_E_ATOTPOPBT_2015","fishnet_E_ATOTPOPBT_2020","fishnet_UNE_ATOTPOPBT_2000",
                  "fishnet_UNE_ATOTPOPBT_2005","fishnet_UNE_ATOTPOPBT_2010","fishnet_UNE_ATOTPOPBT_2015",
                  "fishnet_UNE_ATOTPOPBT_2020"])

print "header is written"

# iterate
for gdb in gdbs:

    # assign null values to value variables
    COUNTRYCODE = None
    CENSUSYEAR = None
    ATOTPOPBT = None
    estimates_E_ATOTPOPBT_2000 = None
    estimates_E_ATOTPOPBT_2005 = None
    estimates_E_ATOTPOPBT_2010 = None
    estimates_E_ATOTPOPBT_2015 = None
    estimates_E_ATOTPOPBT_2020 = None
    estimates_UNE_ATOTPOPBT_2000 = None
    estimates_UNE_ATOTPOPBT_2005 = None
    estimates_UNE_ATOTPOPBT_2010 = None
    estimates_UNE_ATOTPOPBT_2015 = None
    estimates_UNE_ATOTPOPBT_2020 = None
    boundary_E_ATOTPOPBT_2000 = None
    boundary_E_ATOTPOPBT_2005 = None
    boundary_E_ATOTPOPBT_2010 = None
    boundary_E_ATOTPOPBT_2015 = None
    boundary_E_ATOTPOPBT_2020 = None
    boundary_UNE_ATOTPOPBT_2000 = None
    boundary_UNE_ATOTPOPBT_2005 = None
    boundary_UNE_ATOTPOPBT_2010 = None
    boundary_UNE_ATOTPOPBT_2015 = None
    boundary_UNE_ATOTPOPBT_2020 = None
    fishnet_E_ATOTPOPBT_2000 = None
    fishnet_E_ATOTPOPBT_2005 = None
    fishnet_E_ATOTPOPBT_2010 = None
    fishnet_E_ATOTPOPBT_2015 = None
    fishnet_E_ATOTPOPBT_2020 = None
    fishnet_UNE_ATOTPOPBT_2000 = None
    fishnet_UNE_ATOTPOPBT_2005 = None
    fishnet_UNE_ATOTPOPBT_2010 = None
    fishnet_UNE_ATOTPOPBT_2015 = None
    fishnet_UNE_ATOTPOPBT_2020 = None

    arcpy.env.workspace = gdb

    # Get Country code from gdb name
    COUNTRYCODE = os.path.basename(gdb)[:-4]+"_"
    print COUNTRYCODE
    estimatetable = arcpy.ListTables("*estimates")
    boundaryfile = arcpy.ListFeatureClasses("*boundaries*gridding")
    fishnetfile = arcpy.ListFeatureClasses("*fishnet")

# Get the census year from the name of the census file
# This will only work for some countries, will have to fix later
    temp = arcpy.ListTables("*input_population")
    if not len(temp)==0:
        temp_year = temp[0]
        placement = temp_year.find("2")
        if placement > 0:
            CENSUSYEAR = temp_year[placement:placement+4]
    else:
        print "No input_population file found"
    
    
#####################ESTIMATES#########################
    if not len(estimatetable)==0:
        estimates = estimatetable[0]
         # Routine to check that the count fields exist
        searchFields = ["ATOTPOPBT","E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015",
                        "E_ATOTPOPBT_2020","UNE_ATOTPOPBT_2000","UNE_ATOTPOPBT_2005","UNE_ATOTPOPBT_2010",
                        "UNE_ATOTPOPBT_2015","UNE_ATOTPOPBT_2020"]
        cntFields = []
        for field in searchFields:
            checkList = arcpy.ListFields(estimates,field)
            if len(checkList) == 1:
                cntFields.append([field,'SUM'])
            else:
                pass
        # Create temporary table for estimates sums
        sum_temp_estimates = r'C:\Users\jmills\Downloads\tests.gdb' + os.sep + COUNTRYCODE + "estimates"
        if not len(cntFields) == 0:
            arcpy.Statistics_analysis(estimates,sum_temp_estimates,cntFields)
            print "calculated estimates statistics"
            # Get a list of fields from the new in-memory table
            flds = arcpy.ListFields(sum_temp_estimates)
            # Open a Search Cursor using field name
            for fld in flds:
                search = arcpy.SearchCursor(sum_temp_estimates)
                for row in search:
                    if fld.name == "SUM_ATOTPOPBT":
                        #Get the first row with sum value
                        ATOTPOPBT = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2000":
                        #Get the first row with sum value
                        estimates_E_ATOTPOPBT_2000 = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2005":
                        #Get the first row with sum value
                        estimates_E_ATOTPOPBT_2005 = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2010":
                        #Get the first row with sum value
                        estimates_E_ATOTPOPBT_2010 = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2015":
                        #Get the first row with sum value
                        estimates_E_ATOTPOPBT_2015 = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2020":
                        #Get the first row with sum value
                        estimates_E_ATOTPOPBT_2020 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2000":
                        #Get the first row with sum value
                        estimates_UNE_ATOTPOPBT_2000 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2005":
                        #Get the first row with sum value
                        estimates_UNE_ATOTPOPBT_2005 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2010":
                        #Get the first row with sum value
                        estimates_UNE_ATOTPOPBT_2010 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2015":
                        #Get the first row with sum value
                        estimates_UNE_ATOTPOPBT_2015 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2020":
                        #Get the first row with sum value
                        estimates_UNE_ATOTPOPBT_2020 = row.getValue(fld.name)

    else:
        print "No estimates table found"

####################BOUNDARY##########################
    if not len(boundaryfile)==0:
        boundary = boundaryfile[0]
         # Routine to check that the count fields exist
        searchFields = ["E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015",
                        "E_ATOTPOPBT_2020","UNE_ATOTPOPBT_2000","UNE_ATOTPOPBT_2005","UNE_ATOTPOPBT_2010",
                        "UNE_ATOTPOPBT_2015","UNE_ATOTPOPBT_2020"]
        cntFields = []
        for field in searchFields:
            checkList = arcpy.ListFields(boundary,field)
            if len(checkList) == 1:
                cntFields.append([field,'SUM'])
            else:
                pass
        # Create temporary table for gridding sums
        sum_temp_boundary = r'C:\Users\jmills\Downloads\tests.gdb' + os.sep + COUNTRYCODE + "boundary"
        if not len(cntFields) == 0:
            arcpy.Statistics_analysis(boundary,sum_temp_boundary,cntFields)
            print "calculated boundary statistics"
            # Get a list of fields from the new in-memory table
            flds = arcpy.ListFields(sum_temp_boundary)
            # Open a Search Cursor using field name
            for fld in flds:
                search = arcpy.SearchCursor(sum_temp_boundary)
                for row in search:
                    if fld.name == "SUM_E_ATOTPOPBT_2000":
                        #Get the first row with sum value
                        boundary_E_ATOTPOPBT_2000 = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2005":
                        #Get the first row with sum value
                        boundary_E_ATOTPOPBT_2005 = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2010":
                        #Get the first row with sum value
                        boundary_E_ATOTPOPBT_2010 = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2015":
                        #Get the first row with sum value
                        boundary_E_ATOTPOPBT_2015 = row.getValue(fld.name)
                    elif fld.name == "SUM_E_ATOTPOPBT_2020":
                        #Get the first row with sum value
                        boundary_E_ATOTPOPBT_2020 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2000":
                        #Get the first row with sum value
                        boundary_UNE_ATOTPOPBT_2000 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2005":
                        #Get the first row with sum value
                        boundary_UNE_ATOTPOPBT_2005 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2010":
                        #Get the first row with sum value
                        boundary_UNE_ATOTPOPBT_2010 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2015":
                        #Get the first row with sum value
                        boundary_UNE_ATOTPOPBT_2015 = row.getValue(fld.name)
                    elif fld.name == "SUM_UNE_ATOTPOPBT_2020":
                        #Get the first row with sum value
                        boundary_UNE_ATOTPOPBT_2020 = row.getValue(fld.name)

    else:
        print "No gridding boundary found"

#####################FISHNET##########################        
    if not len(fishnetfile)==0:
        fishnet = fishnetfile[0]
         # Routine to check that the count fields exist
        searchFields = ["SUM_E_ATOTPOPBT_2000_CNTM","SUM_E_ATOTPOPBT_2005_CNTM","SUM_E_ATOTPOPBT_2010_CNTM",
                        "SUM_E_ATOTPOPBT_2015_CNTM","SUM_E_ATOTPOPBT_2020_CNTM","SUM_UNE_ATOTPOPBT_2000_CNTM",
                        "SUM_UNE_ATOTPOPBT_2005_CNTM","SUM_UNE_ATOTPOPBT_2010_CNTM",
                        "SUM_UNE_ATOTPOPBT_2015_CNTM","SUM_UNE_ATOTPOPBT_2020_CNTM"]
        cntFields = []
        for field in searchFields:
            checkList = arcpy.ListFields(fishnet,field)
            if len(checkList) == 1:
                cntFields.append([field,'SUM'])
            else:
                pass
        # Create temporary table for fishnet sums
        sum_temp_fishnet = r'C:\Users\jmills\Downloads\tests.gdb' + os.sep + COUNTRYCODE + "fishnet"
        if not len(cntFields) == 0:
            arcpy.Statistics_analysis(fishnet,sum_temp_fishnet,cntFields)
            print "calculated fishnet statistics"
            # Get a list of fields from the new in-memory table
            flds = arcpy.ListFields(sum_temp_fishnet)
            # Open a Search Cursor using field name
            for fld in flds:
                search = arcpy.SearchCursor(sum_temp_fishnet)
                for row in search:
                    if fld.name == "SUM_SUM_E_ATOTPOPBT_2000_CNTM":
                        #Get the first row with sum value
                        fishnet_E_ATOTPOPBT_2000 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_E_ATOTPOPBT_2005_CNTM":
                        #Get the first row with sum value
                        fishnet_E_ATOTPOPBT_2005 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_E_ATOTPOPBT_2010_CNTM":
                        #Get the first row with sum value
                        fishnet_E_ATOTPOPBT_2010 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_E_ATOTPOPBT_2015_CNTM":
                        #Get the first row with sum value
                        fishnet_E_ATOTPOPBT_2015 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_E_ATOTPOPBT_2020_CNTM":
                        #Get the first row with sum value
                        fishnet_E_ATOTPOPBT_2020 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_UNE_ATOTPOPBT_2000_CNTM":
                        #Get the first row with sum value
                        fishnet_UNE_ATOTPOPBT_2000 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_UNE_ATOTPOPBT_2005_CNTM":
                        #Get the first row with sum value
                        fishnet_UNE_ATOTPOPBT_2005 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_UNE_ATOTPOPBT_2010_CNTM":
                        #Get the first row with sum value
                        fishnet_UNE_ATOTPOPBT_2010 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_UNE_ATOTPOPBT_2015_CNTM":
                        #Get the first row with sum value
                        fishnet_UNE_ATOTPOPBT_2015 = row.getValue(fld.name)
                    elif fld.name == "SUM_SUM_UNE_ATOTPOPBT_2020_CNTM":
                        #Get the first row with sum value
                        fishnet_UNE_ATOTPOPBT_2020 = row.getValue(fld.name)

    else:
        print "No fishnet found"

######################################################


    # Check that all the fields have values assigned
    csvFile.writerow([COUNTRYCODE,CENSUSYEAR,ATOTPOPBT,estimates_E_ATOTPOPBT_2000,estimates_E_ATOTPOPBT_2005,
                      estimates_E_ATOTPOPBT_2010,estimates_E_ATOTPOPBT_2015,estimates_E_ATOTPOPBT_2020,
                      estimates_UNE_ATOTPOPBT_2000,estimates_UNE_ATOTPOPBT_2005,estimates_UNE_ATOTPOPBT_2010,
                      estimates_UNE_ATOTPOPBT_2015,estimates_UNE_ATOTPOPBT_2020,
                      boundary_E_ATOTPOPBT_2000,boundary_E_ATOTPOPBT_2005,boundary_E_ATOTPOPBT_2010,
                      boundary_E_ATOTPOPBT_2015,boundary_E_ATOTPOPBT_2020,boundary_UNE_ATOTPOPBT_2000,
                      boundary_UNE_ATOTPOPBT_2005,boundary_UNE_ATOTPOPBT_2010,boundary_UNE_ATOTPOPBT_2015,
                      boundary_UNE_ATOTPOPBT_2020,
                      fishnet_E_ATOTPOPBT_2000,fishnet_E_ATOTPOPBT_2005,fishnet_E_ATOTPOPBT_2010,
                      fishnet_E_ATOTPOPBT_2015,fishnet_E_ATOTPOPBT_2020,fishnet_UNE_ATOTPOPBT_2000,
                      fishnet_UNE_ATOTPOPBT_2005,fishnet_UNE_ATOTPOPBT_2010,fishnet_UNE_ATOTPOPBT_2015,
                      fishnet_UNE_ATOTPOPBT_2020])
    print "Added " + COUNTRYCODE


print "done"







