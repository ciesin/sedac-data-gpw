#-------------------------------------------------------------------------------
# Name:        module1
# Author:      Erin Doxsey-Whitfield
# Created:     17/03/2015
# Purpose:     Fixing attributes in the BRA tables -  4 issues:
#                 1) NAME2 and NAME3 are reversed.  They need to be fixed
#                 2) No UCADMIN fields.  Can be populated using portions of the USCID field
#                 3) NAME5 is blank.  Should be populated with the values from the USCID - not needed in bra.gdb (NAME5 already filled in)
#                 4) Add CENSUS_YEAR (and populate with 2010) - not needed in bra.gdb (NAME5 already filled in)
#-------------------------------------------------------------------------------



# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\bra_state_ERIN_fix'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\fix_BRA_attributes\test'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\fix_BRA_attributes\arcmapPlaying'
arcpy.env.workspace = workspace


# List File GDBs in workspace
gdbList = arcpy.ListWorkspaces("*","FileGDB")


# Iterate through gdbs
for gdb in gdbList:
    arcpy.env.workspace = gdb
    print os.path.basename(gdb)

   
# List tables in each GDB (each table needs to be fixed)
    tableList = arcpy.ListTables("*")
    tableList.sort()
    for table in tableList:
        print "\t" + table

# 1) Reverse NAME2 and NAME3
    # Rename NAME2 and NAME3 to wrong_NAME2 and wrong_NAME3
        arcpy.AlterField_management(table,"NAME2", "wrong_NAME2", "wrong_NAME2")
        arcpy.AlterField_management(table,"NAME3", "wrong_NAME3", "wrong_NAME3")

    #Create the new, correct NAME2 and NAME3 fields
        arcpy.AddField_management(table, "NAME2", "TEXT")
        arcpy.AddField_management(table, "NAME3", "TEXT")


    # Copy what is in NAME2_wrong to NAME3; copy what is in NAME3_wrong to NAME2
        arcpy.CalculateField_management(table,"NAME2","!wrong_NAME3!","PYTHON")
        arcpy.CalculateField_management(table,"NAME3","!wrong_NAME2!","PYTHON")
        print "\t\tNAME2 and NAME3 fields fixed"

##    # Delete wrong_NAME2 and wrong_NAME3 fields (can just run this once you've checked the data)
##        arcpy.DeleteField_management(table,["wrong_NAME2","wrong_NAME3"])
##        print "\t\twrong_NAME2 and wrong_NAME3 fields deleted"

# 2) Add and calculate UCADMIN fields
        # Add UCADMIN fields (one for each NAME field)
        nameFields = arcpy.ListFields(table,"NAME*")
        UCADMINFields = []
        if len(nameFields) == 0:
            UCADMINFields = []
        elif len(nameFields) == 1:
            UCADMINFields = ["UCADMIN0"]
        elif len(nameFields) == 2:
            UCADMINFields = ["UCADMIN0","UCADMIN1"]
        elif len(nameFields) == 3:
            UCADMINFields = ["UCADMIN0","UCADMIN1","UCADMIN2"]
        elif len(nameFields) == 4:
            UCADMINFields = ["UCADMIN0","UCADMIN1","UCADMIN2","UCADMIN3"]
        elif len(nameFields) == 5:
            UCADMINFields = ["UCADMIN0","UCADMIN1","UCADMIN2","UCADMIN3","UCADMIN4"]
        elif len(nameFields) == 6:
            UCADMINFields = ["UCADMIN0","UCADMIN1","UCADMIN2","UCADMIN3","UCADMIN4","UCADMIN5"]
        else:
            print "so many NAME fields!"

        for UCADMINField in UCADMINFields:
            arcpy.AddField_management(table, UCADMINField, "DOUBLE")
        
            
        # Calculate UCADMIN fields using USCID (can parse it)
        # USCID digits: First 2 = UCADMIN1; next 5 = UCADMIN2; next 2 = UCADMIN3; next 2 = UCADMIN4; last 4 = UCADMIN5
        arcpy.CalculateField_management(table,"UCADMIN0","!UCID0!","PYTHON") # 3 -digit ISO - same as UCID0
        arcpy.CalculateField_management(table,"UCADMIN1","!USCID![0:2]","PYTHON") # First 2 digits of USCID (which is the original Sector code from Brazil)                 
        arcpy.CalculateField_management(table,"UCADMIN2","!USCID![2:7]","PYTHON") 
        arcpy.CalculateField_management(table,"UCADMIN3","!USCID![7:9]","PYTHON")
        arcpy.CalculateField_management(table,"UCADMIN4","!USCID![9:11]","PYTHON")
        arcpy.CalculateField_management(table,"UCADMIN5","!USCID![11:15]","PYTHON")

        print "\t\tAdded and calculated {} UCADMIN fields".format(len(UCADMINFields))


            
        if os.path.basename(gdb) != "bra.gdb": # The following tasks don't need to happen for the tables in the bra.gdb
# 3) Calculate NAME5
            arcpy.CalculateField_management(table,"NAME5","!USCID!","PYTHON")
            print "\t\tCalculated NAME5 field"
            
# 4) Add and calculate CENSUS_YEAR
            arcpy.AddField_management(table, "CENSUS_YEAR", "SHORT")
            arcpy.CalculateField_management(table,"CENSUS_YEAR",2010,"PYTHON")
            print "\t\tAdded CENSUS_YEAR field and filled in '2010'"
            

        else:
            print "\t\t(Don't need to calculate NAME5)"
            print "\t\t(Don't need to add CENSUS_YEAR)"
            pass  

print datetime.datetime.now() - startTime
print 'done'



