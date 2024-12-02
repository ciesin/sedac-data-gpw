# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv, datetime

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr_tables.gdb'
tablesOut = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr_extremes.gdb'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
tables = arcpy.ListTables("*")
tables.sort()

# define csv file
attributes =r'\\Dataserver0\gpw\GPW4\Gridding\validation' + os.sep + 'growth_rate_unit_count.csv'
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("COUNTRYCODE","TOTALROWS","ROWSLESSTHANNEG5","ROWSMORETHAN5"))

# iterate
for table in tables:
    startTime = datetime.datetime.now()
           
    # get ISO
    ISO = table[:3]
    agrFields = arcpy.ListFields(table,"agr")
    if len(agrFields)<1:
        print ISO
##    yearFields = arcpy.ListFields(table,"*year")
##    for yearField in yearFields:
##        yrName = yearField.name
##        print yrName
##    # count the number of rows
##    TOTALROWS = arcpy.GetCount_management(table)[0]
##    # select rows with an AGR less than -5%
##    lessThanExpression = "AGR <-0.05"
##    lessThanTable = ISO + "_lessthan_neg5"
##    lessThanOut = tablesOut + os.sep + ISO + "_lessthan_neg5"
##    arcpy.MakeTableView_management(table,lessThanTable,lessThanExpression)
##    # count the number of rows
##    ROWSLESSTHANNEG5 = arcpy.GetCount_management(lessThanTable)[0]
##    # copy to a new table
##    arcpy.CopyRows_management(lessThanTable,lessThanOut)
##    # select rows with an AGR more than 5%
##    moreThanExpression = "AGR > 0.05"
##    moreThanTable = ISO + "_morethan_5"
##    moreThanOut = tablesOut + os.sep + ISO + "_morethan_neg5"
##    arcpy.MakeTableView_management(table,moreThanTable,moreThanExpression)
##    # count the number of rows
##    ROWSMORETHAN5 = arcpy.GetCount_management(moreThanTable)[0]
##    # copy to a new table
##    arcpy.CopyRows_management(moreThanTable,moreThanOut)
##    # Write to csv
##    csvFile.writerow((ISO,TOTALROWS,ROWSLESSTHANNEG5,ROWSMORETHAN5))
##    print "Added statistics pixels for " + ISO
##    print datetime.datetime.now() - startTime
    

