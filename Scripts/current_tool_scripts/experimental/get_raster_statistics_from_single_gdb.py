# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
arcpy.CheckOutExtension("SPATIAL")

# define csv file
attributes = r'\\dataserver0\gpw\GPW4\Gridding\validation' + os.sep + "area_stats_10_17_14.csv"
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("ISO","VARIABLE","MAX","MIN","SUM"))
zone = r'\\Dataserver0\gpw\GPW4\Gridding\global\ancillary\global_30_second_extent.tif'
gdb = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters_v4.0_alpha2\AREA.gdb'
arcpy.env.workspace = gdb
variables = arcpy.ListRasters("*area*")
for variable in variables:
    VARIABLE = variable
    ISO = variable[:3]
    # run zonalstats
    zstat = r'\\Dataserver0\gpw\GPW4\Gridding\validation\area_diagnostics_10_17_14.gdb' + os.sep + VARIABLE + "_statistics"
    if not arcpy.Exists(zstat):
        try:
            arcpy.sa.ZonalStatisticsAsTable(zone,"VALUE",variable,zstat,"DATA","ALL")
            print "Created " + zstat
        except:
            print variable
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
        csvFile.writerow((ISO,VARIABLE,MAX,MIN,SUM))
    print "Added Statistics for " + variable
    

