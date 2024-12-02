# Erin DW
# January 8, 2014


# Import Libraries
import arcpy, os, csv

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
##workspace = r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Admin levels'


# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
# Will have to go back and get data for the countries that are in folders (bra, can, grl, rus, usa)
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# define csv file
attributes =r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Admin levels\admin_levels.csv'

# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))

csvFile.writerow(["COUNTRYCODE","Admin_Level_from_field", "Admin_Level_from_tableName","Match?"])

print "header is written"

# iterate
for gdb in gdbs:

    # assign null values to value variables
    COUNTRYCODE = None
    adminLevel_field = None
    adminLevel_tablename = None
    Match = None

    arcpy.env.workspace = gdb

    # Get Country code from gdb name
    COUNTRYCODE = os.path.basename(gdb)[:-4]
    print COUNTRYCODE

    # Use to skip countries
    if COUNTRYCODE.startswith(())== False:


        # Select input_population Table
        inputTable = arcpy.ListTables("*input_population")
        print "\t" + str(inputTable)


        # Determine the Admin level from the Name fields (i.e. if the highest NAME* field is NAME3, the admin level is 3)
        for table in inputTable:
            fields = arcpy.ListFields(table,"NAME*")
            for field in fields:
                    print "\t" + str(field.name)
##            adminLevel_field = len(fields) - 1
##            print "\tadminLevel_field is: " + str(adminLevel_field)
##            
##        # Determine the Admin level from the input_population Table name (i.e. abw_admin2_2010_input_population)
##            adminLevel_tablename = os.path.basename(table)[9]
##            print "\tadminLevel_tablename is: " + str(adminLevel_tablename)
##            
##        # Determine if the Admin levels match
##        if int(adminLevel_field) - int(adminLevel_tablename) == 0:
##            Match = "YES"
##        else:
##            Match = "NO"
##        print "\tMatch = " + Match
##                
##        # Write values to csv
##        csvFile.writerow([COUNTRYCODE, adminLevel_field, adminLevel_tablename, Match])     

    else:
        print "pass"
    
print 'done'
