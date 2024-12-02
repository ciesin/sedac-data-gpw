# Erin Doxsey-Whitfield
# February 13, 2015
# JRC_delete_fields_join_table.py
    # We want to provide JRC with gridding boundaries (i.e. boundaries with 2010 pop attached)
    # However, the admin names in the gridding boundaries are from the boundaries, not from the census
    # The first script (copy_gridding_boundaries_for_JRC
        # 1. Copies the gridding_boundaries fc and input_pop table for the African countries we are permitted to share to a new gdb in
        #       GPW4/MISC/GPW data for others
        

    # The second script (JRC_delete_fields_join_table.py):    
        # 2. Deletes all fields but UBID, E_ATOTPOPBT_2010, and the 3 AREA fields
        # 3. Joins the USCID, NAME and UCID fields from the input_pop table to the gridding_boundaries fc


    # This script checks the final fields present in the jrc boundaries

    


# Import Libraries
import arcpy, os, csv
from arcpy import env
import datetime
startTime = datetime.datetime.now()

# Define Workspace Variable
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\gridding_gdb_for_JRC\intermediary_files'
workspace = r'\\Dataserver0\gpw\GPW4\MISC\GPW data for others\JRC_GHSLwork\intermediary_files'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# define csv file
output = r'C:\Users\edwhitfi\Desktop\scratch\gridding_gdb_for_JRC\field_info.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("ISO","TOTFIELDS","OBJECTID","SHAPE", "ADMIN", "E_ATOTPOP_BT", "UBID", "USCID", "UCID","NAME", "YEAR", "OTHER"))
                 
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

#iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    
    # Parse ISO
    iso = os.path.basename(gdb)[:-4]
    print iso

#   If only running the script for a portion of the countries is needed:
##    if iso.startswith(('cpv','d','e','g','i','l','m','n','p','r','s','t','u','z')):

    # Copy gridding fc to same GDB (so you can work on a duplicate) - duplicate named: iso_admin#_boundaries_2010
    
    jrc_boundarys = arcpy.ListFeatureClasses("*jrc")
    for jrc_boundary in jrc_boundarys:
        print jrc_boundary
                    
        # List all fields in the JRC boundary   

        OBJECTID = 0
        SHAPE = 0
        ADMIN = 0
        E_ATOTPOP_BT = 0
        UBID = 0
        USCID = 0
        UCID = 0
        NAME = 0
        POP_YEAR = 0
        OTHER = 0

        # Count number of fields in JRC boundary
        jrcFields = arcpy.ListFields(jrc_boundary)
        TOTFIELDS = len(jrcFields)
        print "\tNumber of fields: " + str(len(jrcFields))

        # Count number of fields that fit each category of fields. Sum should add up to TOTFIELDS
        for jrcField in jrcFields:
##            print "\t" + jrcField.name
            
            if jrcField.name.startswith(("OBJECTID")) == True:
                OBJECTID = OBJECTID + 1
            elif jrcField.name.startswith(("Shape","SHAPE")) == True:
                SHAPE = SHAPE + 1
            elif jrcField.name.startswith(("ADMIN")) == True:
                ADMIN = ADMIN + 1
            elif jrcField.name.startswith(("E_ATOTPOPBT_2010")) == True:
                E_ATOTPOP_BT = E_ATOTPOP_BT + 1
            elif jrcField.name.startswith(("USCID")) == True:
                USCID = USCID + 1
            elif jrcField.name.startswith(("UBID")) == True:
                UBID = UBID + 1
            elif jrcField.name.startswith(("UCID")) == True:
                UCID = UCID + 1
            elif jrcField.name.startswith(("NAME")) == True:
                NAME = NAME + 1
            elif jrcField.name.startswith(("POP_YEAR")) == True:
                POP_YEAR = POP_YEAR + 1
            else:
                OTHER = OTHER + 1
                print "\tOther: " + jrcField.name

    # Print data to csv for that gdb. Can check whether any fields are missing based on what fields are expected
        csvFile.writerow((iso,TOTFIELDS,OBJECTID, SHAPE, ADMIN, E_ATOTPOP_BT, UBID, USCID, UCID, NAME, POP_YEAR, OTHER))

## Number of expected fields per category:              
    ##OBJECTID (1)
    ##Shape (3 minimum)
    ##ADMIN (3)
    ##E_ATOTPOP_BT (1)
    ##UBID (1)
    ##USCID (1)
    ##UCID (at least 1) 
    ##NAME (at least 1, must match UCID)
    ##_YEAR (1)


##    else:
##        print "\tAlready run"
    
        
print "Done"                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
