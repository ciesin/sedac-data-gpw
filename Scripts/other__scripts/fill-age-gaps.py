# GPW Census fill age gaps
# Purpose: To Fill in Rows for Missing Ages
# Kytt MacManus
# September 10, 2012

# Import Python Libraries
import arcpy, os
from arcpy import env
from arcpy import da

# Set Overwrite Output Environment
env.overwriteOutput = 1

# Define Workspace
workspace = r"D:\gpw4\ecu\ecu-ingest.gdb"
env.workspace = workspace

# Define input table
table = r"D:\gpw4\ecu\ecu-ingest.gdb\ecu_2010"

# Define Unique Admin Identifier
uid = "UCADMIN3"

# Create Age Summary Table
ageSummary = "ecu_2010_age_summary"
if arcpy.Exists(ageSummary)==True:
    print ageSummary + " already exists"
else:
    try:
        arcpy.Frequency_analysis(table,ageSummary,"AGE")
        print "Created " + ageSummary
    except:
        print arcpy.GetMessages()

# Determine number of unique categories
uniqueCategories = int(str(arcpy.GetCount_management(ageSummary)))
print "There are " + str(uniqueCategories) + " unique categories"

# Create Summary table by uid
uidSummary = "ecu_2010_ucadmin3_summary"
if arcpy.Exists(uidSummary)==True:
    print uidSummary + " already exists"
else:
    try:
        arcpy.Frequency_analysis(table,uidSummary,uid)
        print "Created " + uidSummary
    except:
        print arcpy.GetMessages()

# Create Search Cursor for uidSummary
with da.SearchCursor(uidSummary,uid) as uidSearch:
    for searchRow in uidSearch:        
        adminID = str(searchRow[0])
        print "Evaluating: " + adminID
        whereclause = '"' + uid + '" =' + "'" + adminID + "'"
        # Create Search Cursor for ageSummary
        with da.SearchCursor(ageSummary,"AGE") as ageSearch:
            for ageSearchRow in ageSearch:
                ageSearchValue = str(ageSearchRow[0])
##                print "AGE LOOKUP: " + ageSearchValue                
                # Create Search Cursor for table
                with da.SearchCursor(table,("AGE"), whereclause) as tableSearch:
                    for tableSearchRow in tableSearch:
##                        nameValue = str(tableSearchRow[0])
                        ageValue = str(tableSearchRow[0])
##                        print "AGE VALUE: " + ageValue                
                        if ageSearchValue == ageValue:
##                            print "Age exists in table"
                            break
                    else:
##                        print "The loop finished without a match"
                        # Create Insert Cursor to add Missing Row
                        tableInsert = da.InsertCursor(table,("AGE","UCADMIN3"))
                        tableInsert.insertRow((ageSearchValue,adminID))
##                        print "Inserted Row for " +  adminID + " AGE: " + ageSearchValue
                        del tableInsert                           
                
##        break
                
