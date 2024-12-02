# this script calculates the age 5 year proportions table
# because ATOTPOPBT does not necessarily equal
# the the sum of ages, a proxy total is calculated by
# adding the ages structure variables
# this proxy total forms the basis for the derivation of proportions
 
import os
import re
import multiprocessing
import arcpy
import imp, sys
 
def calcAgeProportions(gdb):
    '''Worker function'''
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        return "VCS doesn't gave age data"
    else:
        # define files to work with
        ageFile = arcpy.ListTables("*age_5_year_input")[0]
        ageProportions = gdb + os.sep + ageFile.replace("_input","_proportions")        
        # check if the ageProportions is already existing
        if arcpy.Exists(ageProportions):
            return ageProportions + " already exists"
##            arcpy.Delete_management(ageProportions)
##            print "Deleted " + ageProportions
        else:
            # first preprocess the ageFile
            # create output table
            arcpy.CopyRows_management(ageFile,ageProportions)
            # add and calculate CALC_ATOTPOPBT as sum(ageVariables)
            # to ensure that the denominator results in proportions that
            # sum to 1
            arcpy.AddField_management(ageProportions,"CALC_ATOTPOPBT_AGE","LONG")
            arcpy.CalculateField_management(ageProportions,"CALC_ATOTPOPBT_AGE",
                                            "!A000_004BT!+!A005_009BT!+!A010_014BT!+!A015_019BT!+"
                                            + "!A020_024BT!+!A025_029BT!+!A030_034BT!+!A035_039BT!+"
                                            + "!A040_044BT!+!A045_049BT!+!A050_054BT!+!A055_059BT!+"
                                            + "!A060_064BT!+!A065_069BT!+!A070_074BT!+!A075_079BT!+"
                                            + "!A080_084BT!+!A085plusBT!","PYTHON")
            # create table view to avoid division by 0
            vTable = os.path.basename(ageProportions) + "_VIEW"
            vExpression = '"CALC_ATOTPOPBT_AGE" > 0'
            arcpy.MakeTableView_management(ageProportions, vTable, vExpression)
                                      
            # create list of age variables and cycle
            ageVariables = ["!A000_004BT!","!A005_009BT!","!A010_014BT!","!A015_019BT!","!A020_024BT!",
                            "!A025_029BT!","!A030_034BT!","!A035_039BT!","!A040_044BT!","!A045_049BT!",
                            "!A050_054BT!","!A055_059BT!","!A060_064BT!","!A065_069BT!","!A070_074BT!",
                            "!A075_079BT!","!A080_084BT!","!A085plusBT!"]
            for ageVariable in ageVariables:
                rawAgeVariable = ageVariable.replace("!","")
                rawPropVariable = rawAgeVariable + "PROP"
                # add prop fields and calculate
                arcpy.AddField_management(vTable,rawPropVariable,"DOUBLE")
                pCalc = "float(" + ageVariable + ")/float(!CALC_ATOTPOPBT_AGE!)"
                arcpy.CalculateField_management(vTable,rawPropVariable,pCalc,"PYTHON")
                # create table view to fill in nulls
                # define view
                view0 = os.path.basename(ageProportions) + "_" + rawAgeVariable + "_NULL"
                # define calculation expression
                expression0 = '"CALC_ATOTPOPBT_AGE" = 0' 
                arcpy.MakeTableView_management(ageProportions, view0, expression0)
                arcpy.CalculateField_management(view0, rawPropVariable, "0", "PYTHON")            
            return "Calculated age proportions for " + gdb
        
 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'H:\gpw\pop_tables'
    usaSpace = workspace + os.sep + r"usa"
    braSpace = workspace + os.sep + r"bra"
    canSpace = workspace + os.sep + r"can"
    grlSpace = workspace + os.sep + r"grl"
    rusSpace = workspace + os.sep + r"rus"
    workspaces = [workspace]#,braSpace,canSpace,grlSpace,rusSpace]#usaSpace,
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt) 
    
##    print len(gdb_list)
##
##    for i in gdb_list:
##        print i 
##
##    for gdbItem in gdb_list:
##        print gdbItem
##        calcageProportions(gdbItem)
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
    try:
        print pool.map(calcAgeProportions, gdb_list)
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool.close()
        pool.join()
    except:
        print sys.stdout
        pool.close()
        pool.join()
        
    # End main
    
 
if __name__ == '__main__':
    main()
