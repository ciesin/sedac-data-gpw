# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv

# Define Workspace Variable
workspace = r'E:\gpw\bra_state\rasters'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
arcpy.CheckOutExtension("SPATIAL")
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# define csv file
attributes = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\bra_state\validation' + os.sep + "bra_raster_stats_9_18_14_v1.csv"
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("ISO","FILE","STATE","VARIABLE","ESTIMATE","YEAR","MAX","MIN","SUM"))

# iterate
for gdb in gdbs:    
    # define zone
    zone = r'\\Dataserver0\gpw\GPW4\Gridding\global\ancillary\global_30_second_extent.tif'
    # list variables
    arcpy.env.workspace = gdb
    files = arcpy.ListRasters("*ATOTPOPBT_2010*")
    for f in files:
        FILE = f
        split = FILE.split("_")
        ISO = split[0]
        STATE = split[1]
        VARIABLE = split[2] + "_" + split[3] + "_" + split[4] + "_" + split[5]
        ESTIMATE = split[2]
        YEAR = split[4]
        
        # run zonalstats
        zstat = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\bra_state\validation\diagnostics3.gdb' + os.sep + f + "_statistics"
        if not arcpy.Exists(zstat):
            try:
                arcpy.sa.ZonalStatisticsAsTable(zone,"VALUE",f,zstat,"DATA","ALL")
##                print "Created " + zstat
            except:
                print arcpy.GetMessages()
                print f
                continue
        
        # create search cursor to grab info from zstat
        fields = ['MAX', 'MIN', 'SUM']
        # For each row print the WELL_ID and WELL_TYPE fields, and the
        # the feature's x,y coordinates
        with arcpy.da.SearchCursor(zstat, fields) as cursor:
            for row in cursor:
                MAX = row[0]
                MIN = row[1]
                SUM = row[2]
                
            csvFile.writerow((ISO,FILE,STATE,VARIABLE,ESTIMATE,YEAR,MAX,MIN,SUM))
    print "Added Statistics for " + ISO
    

