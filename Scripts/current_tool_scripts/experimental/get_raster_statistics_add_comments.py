# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv, datetime
# set start time
startTime = datetime.datetime.now()
# check out SPATIAL extension
arcpy.CheckOutExtension("SPATIAL")
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters_v4.0_alpha2'
# define date variable
date = "11_3_14"
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# create output gdb
# parse parameters
outRoot = r'\\Dataserver0\gpw\GPW4\Gridding\validation'
outGDBName = "raster_diagnostics_" + date
outGDB = outRoot + os.sep + outGDBName + ".gdb"
# if outGDB doesn't exist then create it
if not arcpy.Exists(outGDB):
    try:
        arcpy.CreateFileGDB_management(outRoot,outGDBName)
        print "Created " + outGDB
    except:
        print arcpy.GetMessages()
else:
    print outGDB + " already exists"
# define csv file
attributes = r'\\dataserver0\gpw\GPW4\Gridding\validation' + os.sep + "stats_" +  date + ".csv"
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("ISO","VARIABLE","MAX","MIN","SUM"))
zone = r'\\Dataserver0\gpw\GPW4\Gridding\global\ancillary\global_30_second_extent.tif'
# list gdbs
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
# sort ascending
gdbs.sort()
# iterate
for gdb in gdbs:
    gdbTime = datetime.datetime.now()
    # set env.workspace to gdb
    arcpy.env.workspace = gdb
    # list the rasters
    variables = arcpy.ListRasters("*")
    for variable in variables:
        # parse variable and country descriptors
        VARIABLE = variable[4:]
        ISO = variable[:3]
        # run zonalstats
        zstat = outGDB + os.sep + ISO + "_" + VARIABLE + "_statistics"
        if not arcpy.Exists(zstat):
            try:
                arcpy.sa.ZonalStatisticsAsTable(zone,"VALUE",variable,zstat,"DATA","ALL")
                print "Created " + zstat
            except:
                print variable + " failed"
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
    print "Added Statistics for " + gdb
    print datetime.datetime.now() - gdbTime
print "Completed script"
print datetime.datetime.now() - startTime
        

