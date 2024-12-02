# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\un_adjustment_tables.gdb'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# List tables in workspace environment
tables = arcpy.ListTables("*")
tables.sort()

# define csv file
attributes = r'\\dataserver0\gpw\GPW4\Gridding\validation' + os.sep + "un_adjustment_stats_9_19_14_v2.csv"
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("ISO","UNPOP2000","UNPOP2005","UNPOP2010","UNPOP2015",
                  "UNPOP2020","E_ATOTPOPBT_2000","E_ATOTPOPBT_2005",
                  "E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020",
                  "UNADJFAC_2000","UNADJFAC_2005","UNADJFAC_2010",
                  "UNADJFAC_2015","UNADJFAC_2020"))

# iterate
for table in tables:
    print "Processing " + table
    # create search cursor
    searchFields = ["ISO","UNPOP2000","UNPOP2005","UNPOP2010","UNPOP2015",
                    "UNPOP2020","E_ATOTPOPBT_2000","E_ATOTPOPBT_2005",
                    "E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020",
                    "UNADJFAC_2000","UNADJFAC_2005","UNADJFAC_2010",
                    "UNADJFAC_2015","UNADJFAC_2020"]
    with arcpy.da.SearchCursor(table,searchFields) as searchCursor:
        for row in searchCursor:
            # grab values
            ISO = row[0]
            UNPOP2000 = row[1]
            UNPOP2005 = row[2]
            UNPOP2010 = row[3]
            UNPOP2015 = row[4]
            UNPOP2020 = row[5]
            E_ATOTPOPBT_2000 = row[6]
            E_ATOTPOPBT_2005 = row[7]
            E_ATOTPOPBT_2010 = row[8]
            E_ATOTPOPBT_2015 = row[9]
            E_ATOTPOPBT_2020 = row[10]
            UNADJFAC_2000 = row[11]
            UNADJFAC_2005 = row[12]
            UNADJFAC_2010 = row[13]
            UNADJFAC_2015 = row[14]
            UNADJFAC_2020 = row[15]
            # write values to CSV
            csvFile.writerow((ISO,UNPOP2000,UNPOP2005,UNPOP2010,UNPOP2015,
                  UNPOP2020,E_ATOTPOPBT_2000,E_ATOTPOPBT_2005,
                  E_ATOTPOPBT_2010,E_ATOTPOPBT_2015,E_ATOTPOPBT_2020,
                  UNADJFAC_2000,UNADJFAC_2005,UNADJFAC_2010,
                  UNADJFAC_2015,UNADJFAC_2020))
    print "Added Statistics for " + ISO
    

