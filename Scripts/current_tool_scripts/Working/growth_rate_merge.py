# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv, datetime

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr_tables.gdb'
tablesOut = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr_clean_tables.gdb'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
tables = arcpy.ListTables("*")
tables.sort()

### define csv file
##attributes =r'\\Dataserver0\gpw\GPW4\Gridding\validation' + os.sep + 'growth_rate_merge.csv'
### open csv file and write header
##csvFile = csv.writer(open(attributes,'wb'))
##csvFile.writerow(("ISO","TOTALROWS","USCID","UBID","NAME1","NAME2","NAME3","NAME4","NAME5",
##                  "POPYEAR","ATOTPOPBT","ALTYEAR","ALTPOP","ALTSOURCE","AGR","YEARTO2000",
##                  "YEARTO2005","YEARTO2010","YEARTO2015","YEARTO2020"))
cursorFields = ["USCID","UBID","NAME0","NAME1","NAME2","NAME3","NAME4","NAME5","POPYEAR",
                "UCADMIN0","UCADMIN1","UCADMIN2","UCADMIN3","UCADMIN4","UCADMIN5","ID","OBJECTID","OBJECTID_1",
                "ATOTPOPBT","ALTYEAR","ALTPOP","ALTSOURCE","AGR","YEARTO2000","YEARTO2005",
                "YEARTO2010","YEARTO2015","YEARTO2020","CENSUS_YEAR","CENSUSYEAR","ESTIMATE_YEAR"]

### Create a fieldinfo object
##fieldinfo = arcpy.FieldInfo()
##for cursorField in cursorFields:
##    fieldinfo.addField(cursorField,cursorField,"VISIBLE","NONE")
# iterate
for table in tables:
    startTime = datetime.datetime.now()          
    # get ISO
    ISO = table[:3]

    fields = arcpy.ListFields(table,"*")
    for field in fields:
        fldName = field.name
        if fldName in cursorFields:
            pass
        else:
            print "Delete " + fldName
            arcpy.DeleteField_management(table,fldName)
    
##    # create table view with fieldinfo fields
##    tableView = ISO + "_view"
##    tableOut = tablesOut + os.sep + ISO + "_growth_rate"
##    arcpy.MakeTableView_management(table,tableView,"#","#",fieldinfo)
##    # copy to a new table
##    arcpy.CopyRows_management(tableView,tableOut)
    print "Deleted Fields for " + ISO
    print datetime.datetime.now() - startTime
    
    
##    # count the number of rows
##    TOTALROWS = arcpy.GetCount_management(table)[0]
##    # parse fields
##    for cursorField in cursorFields:
##        # check if the field exists
##        fieldCheck = arcpy.ListFields(table,cursorField)
##        if len(fieldCheck)<>1:
##            print cursorField    
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
    

