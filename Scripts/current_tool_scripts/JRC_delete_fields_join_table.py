# Erin Doxsey-Whitfield
# February 13, 2015
# JRC_delete_fields_join_table.py
    # We want to provide JRC with gridding boundaries (i.e. boundaries with 2010 pop attached)
    # However, the admin names in the gridding boundaries are from the boundaries, not from the census
    # The first script (JRC_copy_gridding_boundaries)
        # 1. Copies the gridding_boundaries fc and input_pop table for the African countries we are permitted to share to a new gdb in
        #       GPW4/MISC/GPW data for others
        

    # This script (JRC_delete_fields_join_table.py):    
        # 2. Deletes all fields but UBID, E_ATOTPOPBT_2010, and the 3 AREA fields
        # 3. Joins the USCID, NAME and UCID fields from the input_pop table to the gridding_boundaries fc


# Import Libraries
import arcpy, os
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

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

#iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    # Parse ISO
    iso = os.path.basename(gdb)[:-4]
    print iso

    if iso.startswith(('cpv','d','e','g','i','l','m','n','p','r','s','t','u','z')):

        # Copy gridding fc to same GDB (so you can work on a duplicate) - duplicate named: iso_admin#_boundaries_2010
        
        gridding_fcs = arcpy.ListFeatureClasses("*gridding")
        for gridding_fc in gridding_fcs:
            print "\t" + gridding_fc

            jrc_boundary = gdb + os.sep + gridding_fc.rstrip("_gridding")+"_jrc"
            arcpy.Copy_management(gridding_fc, jrc_boundary)
            print "\tCopied gridding fc"


        
            # List all fields in the JRC boundary   

            allFields = arcpy.ListFields(jrc_boundary)

            # List wanted fields from the JRC boundary
            inFields = ["UBID", "E_ATOTPOPBT_2010", "ADMINAREAKM", "ADMINWATERAREAKM", "ADMINAREAKMMASKED"]

            # If a field is unwanted and not required, add to dropFieldNameList
            dropFieldNameList = []
            print "\tFields in JRC boundaries:"
            for allField in allFields:
                if allField.name in inFields:
                    print "\t\t" + allField.name + ": in inFields"
                elif allField.required:
                    print "\t\t" + allField.name + ": required"
                else:
                    dropFieldNameList.append(allField.name)
                    print "\t\t" + allField.name + ": is a drop field"

            
            # Delete all fields in dropFieldNameList from JRC boundary       
                    
            arcpy.DeleteField_management(jrc_boundary,dropFieldNameList)
            print "\tFields deleted from JRC boundaries"
            jrcFields = arcpy.ListFields(jrc_boundary)
            print "\t\t\t\tNumber of fields left in JRC boundaries:" + str(len(jrcFields))


        # List all fields in the input_population table

        popTables = arcpy.ListTables("*input_population")

        for popTable in popTables:
            allPopFields = arcpy.ListFields(popTable)
            joinFields = []
            print "\tListed all fields in input_population table"

        # Select fields from table to join to JRC boundaries (want:  USCID, all UCID fields, all NAME fields, and the CENSUS_YEAR or ESTIMATE_YEAR field)
            for allPopField in allPopFields:
                if allPopField.name.startswith(("USCID")) == True:
                    joinFields.append(allPopField.name)
                    print "\t\t" + allPopField.name + ": added to Join Fields"
                elif allPopField.name.startswith(("UCID")) == True:
                    joinFields.append(allPopField.name)
                    print "\t\t" + allPopField.name + ": added to Join Fields"
                elif allPopField.name.startswith(("NAME")) == True:
                    joinFields.append(allPopField.name)
                    print "\t\t" + allPopField.name + ": added to Join Fields"
                elif allPopField.name.endswith(("YEAR")) == True:
                    joinFields.append(allPopField.name)
                    print "\t\t" + allPopField.name + ": added to Join Fields"
                else:
                    print "\t\t" + allPopField.name + ": not needed"
                    

        # Join the wanted fields from the input_pop table to the JRC boundaries

            arcpy.JoinField_management(jrc_boundary,"UBID", popTable, "UBID", joinFields)
            print "\tPop Table fields joined to JRC boundaries"


    else:
        print "\tAlready run"
    
        
print "Done"                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
