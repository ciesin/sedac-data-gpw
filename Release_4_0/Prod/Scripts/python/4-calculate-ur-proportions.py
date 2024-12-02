# this script calculates the ur 5 year proportions table
# because ATOTPOPBT does not necessarily equal
# the the sum of urs, a proxy total is calculated by
# adding the urs structure variables
# this proxy total forms the basis for the derivation of proportions
 
import os
import re
import multiprocessing
import arcpy
import imp, sys
 
def calcurProportions(gdb):
    '''Worker function'''
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        return "VCS doesn't gave ur data"
    else:
        # define files to work with
        urFile = arcpy.ListTables("*ur_input")[0]
        urProportions = gdb + os.sep + urFile.replace("_input","_proportions")        
        # check if the urProportions is already existing
        if arcpy.Exists(urProportions):
            return urProportions + " already exists"
##            arcpy.Delete_manurment(urProportions)
##            print "Deleted " + urProportions
        else:
            # first preprocess the urFile
            # create output table
            arcpy.CopyRows_management(urFile,urProportions)
            # add and calculate CALC_ATOTPOPBT as sum(urVariables)
            # to ensure that the denominator results in proportions that
            # sum to 1
            arcpy.AddField_management(urProportions,"CALC_ATOTPOPBT_UR","DOUBLE")
            arcpy.CalculateField_management(urProportions,"CALC_ATOTPOPBT_UR",
                                            "!ATOTPOPBU!+!ATOTPOPBR!"
                                            ,"PYTHON")
            # create table view to avoid division by 0
            vTable = os.path.basename(urProportions) + "_VIEW"
            vExpression = '"CALC_ATOTPOPBT_UR" > 0'
            arcpy.MakeTableView_management(urProportions, vTable, vExpression)
                                      
            # create list of ur variables and cycle
            urVariables = ["!ATOTPOPBU!","!ATOTPOPBR!","!ATOTPOPFU!",
                           "!ATOTPOPFR!","!ATOTPOPMR!","!ATOTPOPMU!",]
            for urVariable in urVariables:
                rawurVariable = urVariable.replace("!","")
                rawPropVariable = rawurVariable + "_PROP"
                # add prop fields and calculate
                arcpy.AddField_management(vTable,rawPropVariable,"DOUBLE")
                pCalc = "float(" + urVariable + ")/float(!CALC_ATOTPOPBT_UR!)"
                arcpy.CalculateField_management(vTable,rawPropVariable,pCalc,"PYTHON")
                # create table view to fill in nulls
                # define view
                view0 = os.path.basename(urProportions) + "_" + rawurVariable + "_NULL"
                # define calculation expression
                expression0 = '"CALC_ATOTPOPBT_UR" = 0' 
                arcpy.MakeTableView_management(urProportions, view0, expression0)
                arcpy.CalculateField_management(view0, rawPropVariable, "0", "PYTHON")            
            return "Calculated ur proportions for " + gdb
        
 
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
##        calcurProportions(gdbItem)
    pool = multiprocessing.Pool(processes=11,maxtasksperchild=1)
    try:
        print pool.map(calcurProportions, gdb_list)
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
