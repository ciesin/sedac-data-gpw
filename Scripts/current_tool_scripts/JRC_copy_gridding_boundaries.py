# Erin Doxsey-Whitfield
# February 13, 2015
# Copy gridding boundaries for JRC
    # We want to provide JRC with gridding boundaries (i.e. boundaries with 2010 pop attached)
    # However, the admin names in the gridding boundaries are from the boundaries, not from the census
    # This script:
        # 1. Copies the gridding_boundaries fc and input_pop table for the African countries we are permitted to share to a new gdb
        # 2. Deletes all fields but UBID, E_ATOTPOPBT_2010, and the 3 AREA fields
        # 3. Joins the USCID, NAME and UCADMIN fields from the input_pop table to the gridding_boundaries fc


# Import Libraries
import arcpy, os
from arcpy import env
import datetime
startTime = datetime.datetime.now()

# Define Workspace Variable
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\gridding_gdb_for_JRC\inputs'
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

#iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    # Parse ISO
    iso = os.path.basename(gdb)[:-4]
    print iso

    wanted_countries = ['ago','bdi','ben','bfa','bwa','caf','civ','cmr','cod','cog','com','cpv','dji','dza','egy','eri','esh',
                        'eth','gab','gin','gmb','gnb','gnq','lbr','lby','lso','mar','moz','mrt','mus','nam','ner','nga','reu',
                        'rwa','sdn','sen','shn','sle','som','ssd','stp','swz','syc','tgo','tun','tza','uga','zaf','zmb','zwe',
                        'ita','prt']
    
    if iso in wanted_countries:

        # Create temporary <ISO> GDB to store Table and boundaries
##        out_folder = r'C:\Users\edwhitfi\Desktop\scratch\gridding_gdb_for_JRC\intermediary_files'
        out_folder = r'\\Dataserver0\gpw\GPW4\MISC\GPW data for others\JRC_GHSLwork\intermediary_files'
        iso_gdb = out_folder + os.sep + iso + ".gdb"
        print "\t" + iso_gdb 

        if arcpy.Exists(iso_gdb):
            print "\t" + iso + ".gdb already exists"
        else:
            arcpy.CreateFileGDB_management(out_folder, iso)
            print "\tCreated " + iso + " GDB"
            

        # Copy input table to <ISO> gdb
        tables = arcpy.ListTables("*input_population*")
        for table in tables:
            print "\t" + table

            out_data1 = iso_gdb + os.sep + table
            arcpy.Copy_management(table, out_data1)
            print "\tCopied input table"

        # Copy gridding_boundaries feature class to <ISO> gdb
        gridding_fcs = arcpy.ListFeatureClasses("*gridding")
        for gridding_fc in gridding_fcs:
            print "\t" + gridding_fc
            
            out_data2 = iso_gdb + os.sep + gridding_fc
            arcpy.Copy_management(gridding_fc, out_data2)
            print "\tCopied gridding fc"


        
##        inFields = ["UBID", "E_ATOTPOPBT_2010", "ADMINAREAKM", "ADMINWATERAREAKM", "ADMINAREAKMMASKED"]
##        fm = arcpy.FieldMappings()
##        fieldMap = arcpy.FieldMap()
##        for field in fieldList:
##            


            

    else:
        print "\t pass: " + iso + " not in wanted countries" + "\t"
        
print "Done"                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
