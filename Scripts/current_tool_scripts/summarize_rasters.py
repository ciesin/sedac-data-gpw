# Kytt MacManus
# July 28, 2014
# Script to read the files on the network and summarize which census variables are present

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# define csv file
attributes =r'\\Dataserver0\gpw\GPW4\Gridding\validation' + os.sep + 'rasters_on_share_v4.csv'
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("COUNTRYCODE","RASTER","VARIABLE"))

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*_grids.gdb","FILEGDB")
gdbs.sort()
# iterate
for gdb in gdbs:
    print gdb
    arcpy.env.workspace = gdb
    # parse COUNTRYCODE
    COUNTRYCODE = os.path.basename(gdb)[:3]
    # grab rasters
    rasters = arcpy.ListRasters("*TOTPOPBT*")
    # iterate
    for RASTER in rasters:
        VARIABLE = RASTER[4:]
        csvFile.writerow((COUNTRYCODE,RASTER,VARIABLE))
        
               
print datetime.datetime.now() - startTime
