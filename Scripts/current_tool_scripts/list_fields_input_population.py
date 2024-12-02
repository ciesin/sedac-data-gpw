# Erin Doxsey-Whitfield
# February 23, 2015
# list_fields_input_population.py

# Lists all the current fields in the beta gridding input_population tables


# Import Libraries
import arcpy, os, csv
from arcpy import env
import datetime
startTime = datetime.datetime.now()

# Define Workspace Variable
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\rearranging_gridding\inputs'
##workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\grl_municipality'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# define csv file
output = r'C:\Users\edwhitfi\Desktop\scratch\rearranging_gridding\fieldNameList.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("ISO","FieldNames"))


# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

#iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    # Parse ISO
    iso = os.path.basename(gdb)[:-4]
    print iso

    
    # List all fields in the input_population table

    popTables = arcpy.ListTables("*input_population")
    if len(popTables) == 1:
        for popTable in popTables:          
            fieldNames = [str(f.name) for f in arcpy.ListFields(popTable)]
            fieldNames.sort()
            print fieldNames

    else:
        print "\t------RENAME INPUT POP TABLE------"
        fieldNames = []
        
        
        # Print data to csv for that gdb. Can check whether any fields are missing based on what fields are expected
        csvFile.writerow((iso,fieldNames))


        
    
        




    

##    for popTable in popTables:
##        allPopFields = arcpy.ListFields(popTable)
##        joinFields = []
##        print "\tListed all fields in input_population table"
##
##    # Select fields from table to join to JRC boundaries (want:  USCID, all UCID fields, all NAME fields, and the CENSUS_YEAR or ESTIMATE_YEAR field)
##        for allPopField in allPopFields:
##            if allPopField.name.startswith(("USCID")) == True:
##                joinFields.append(allPopField.name)
##                print "\t\t" + allPopField.name + ": added to Join Fields"
##            elif allPopField.name.startswith(("UCID")) == True:
##                joinFields.append(allPopField.name)
##                print "\t\t" + allPopField.name + ": added to Join Fields"
##            elif allPopField.name.startswith(("NAME")) == True:
##                joinFields.append(allPopField.name)
##                print "\t\t" + allPopField.name + ": added to Join Fields"
##            elif allPopField.name.endswith(("YEAR")) == True:
##                joinFields.append(allPopField.name)
##                print "\t\t" + allPopField.name + ": added to Join Fields"
##            else:
##                print "\t\t" + allPopField.name + ": not needed"
##                
##
##    # Join the wanted fields from the input_pop table to the JRC boundaries
##
##        arcpy.JoinField_management(jrc_boundary,"UBID", popTable, "UBID", joinFields)
##        print "\tPop Table fields joined to JRC boundaries"




        
print "Done"                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
