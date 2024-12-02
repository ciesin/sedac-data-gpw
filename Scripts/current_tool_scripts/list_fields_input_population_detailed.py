# Erin Doxsey-Whitfield
# February 23, 2015
# list_fields_input_population_detailed.py

# Lists (and categorizes) all the current fields in the beta gridding input_population tables


# Import Libraries
import arcpy, os, csv
from arcpy import env
import datetime
startTime = datetime.datetime.now()

# Define Workspace Variable
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\rearranging_gridding\inputs'
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'


# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# define csv file
output = r'C:\Users\edwhitfi\Desktop\scratch\rearranging_gridding\fieldNameList.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("ISO","NumFields", "ID", "USCID", "UBID", "YEAR", "NAME", "UCADMIN", "UCID", "ATOTPOPBT", "OtherAGE", "OtherFIELDS"))


# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

#iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    # Parse ISO
    iso = os.path.basename(gdb)[:-4]
    print iso


    # Create empty lists for field names
    ID = []
    USCID = []
    UBID = []
    YEAR = []
    NAME = []
    UCADMIN = []
    UCID = []
    ATOTPOPBT = []
    otherAGE = []
    otherFIELDS = []

    # List all fields in the input_population table

    popTables = arcpy.ListTables("*input_population")
    if len(popTables) == 1:
        for popTable in popTables:          
            fields = arcpy.ListFields(popTable)
            fields.sort()

    # Return number of fields
            numFields = len(fields)
            print "\tFields in " + iso + " input pop table: " + str(numFields)
    #Append each field name to a categorical list
            for field in fields:

                if field.name == "ID":
                    ID.append(str(field.name))
                elif field.name == "USCID":
                    USCID.append(str(field.name))
                elif field.name == "UBID":
                    UBID.append(str(field.name))
                elif field.name.endswith(("YEAR")) == True:
                    YEAR.append(str(field.name))
                elif field.name.startswith(("NAME")) == True:
                    NAME.append(str(field.name))
                elif field.name.startswith(("UCADMIN")) == True:
                    UCADMIN.append(str(field.name))
                elif field.name.startswith(("UCID")) == True:
                    UCID.append(str(field.name))
                elif field.name == "ATOTPOPBT":
                    ATOTPOPBT.append(str(field.name))
                elif field.name.startswith(("A")) == True:
                    otherAGE.append(str(field.name))
                else:
                    otherFIELDS.append(str(field.name))

            print "\tFields categorized"

    else:
        print "\t------RENAME INPUT POP TABLE------"
        numFields = []
        
        
    # Print data to csv for that gdb. 
    csvFile.writerow((iso,numFields, ID, USCID, UBID, YEAR, NAME, UCADMIN, UCID, ATOTPOPBT, otherAGE, otherFIELDS))




        
print "Done"                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
