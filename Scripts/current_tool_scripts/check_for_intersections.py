# Kytt MacManus
# July 24 2014
# Copy Grids to 

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
outRoot = r'\\Dataserver0\gpw\GPW4\Gridding\validation\self_intersections.gdb'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()
# define csv file
attributes = r'\\dataserver0\gpw\GPW4\Gridding\validation' + os.sep + "self_intersections_10_17_14.csv"
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("ISO","UBID"))
# iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    # Parse COUNTRYCODE
    COUNTRYCODE = os.path.basename(gdb)[:3].upper()
    if COUNTRYCODE == "MAC":
        continue
    if COUNTRYCODE == "KIR":
        fcs = arcpy.ListFeatureClasses("kir_*boundaries_2010")
    else:
        # grab boundary
        fcs = arcpy.ListFeatureClasses("*boundaries_2010")
    fc = fcs[0]
    # intersect
    intersectOut = outRoot + os.sep + COUNTRYCODE
    if COUNTRYCODE == "AND":
        intersectOut = outRoot + os.sep + "ANDORRA"
    try:
        arcpy.Intersect_analysis([fc,fc],intersectOut)
        print "Created " + intersectOut
    except:
        print arcpy.GetMessages()
    # summarize
    summaryOut = outRoot + os.sep + COUNTRYCODE + "_summary"
    try:
        arcpy.Frequency_analysis(intersectOut,summaryOut,"UBID")
        print "Created " + summaryOut
    except:
        print arcpy.GetMessages()
    # make table view
    tableView = COUNTRYCODE + "_tv"
    try:
        arcpy.MakeTableView_management(summaryOut,tableView,
                                       """ "FREQUENCY" > 1 """)
        print "Made Table View"
    except:
        print arcpy.GetMessages()
    if int(arcpy.GetCount_management(tableView)[0])>0:
        # copy rows
        outTable = summaryOut + "_errors"
        try:
            arcpy.CopyRows_management(tableView,outTable)
            print "Created " + outTable
        except:
            print arcpy.GetMessages()
        # create search cursor
        with arcpy.da.SearchCursor(outTable, "UBID") as cursor:
            for row in cursor:
                UBID = str(row[0])
                csvFile.writerow((COUNTRYCODE,UBID))
    else:
        print "No self intersections in " + COUNTRYCODE
                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
