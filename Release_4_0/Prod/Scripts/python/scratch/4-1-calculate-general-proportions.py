# this script calculates the proportions of a table
# because the Total Field does not necessarily equal the sum of the variables
# due to various reasons in a given census, it is necessary to derive a specific
# denominator for each group of variables that should be combined
# the reported total population, a proxy total is calculated by
# adding the reported males and females
# this proxy total forms the basis for the derivation of proportions
 
import os
import re
import multiprocessing
import arcpy
import imp, sys
 
def calcSexProportions(gdb):
    '''Worker function'''
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        return "VCS doesn't gave sex data"
    else:
        # define files to work with
        sexFile = arcpy.ListTables("*sex_variables_input")[0]
        sexProportions = gdb + os.sep + sexFile.replace("_input","_proportions")        
        # check if the sexProportions is already existing
        if arcpy.Exists(sexProportions):
            return sexProportions + " already exists"
##            arcpy.Delete_management(sexProportions)
##            print "Deleted " + sexProportions
        else:
            # first preprocess the sexFile
            # create output table
            arcpy.CopyRows_management(sexFile,sexProportions)
            # add and calculate CALC_ATOTPOPBT as ATOTPOPFT + ATOTPOPMT
            # to ensure that the denominator results in proportions that
            # sum to 1
            arcpy.AddField_management(sexProportions,"CALC_ATOTPOPBT","LONG")
            arcpy.CalculateField_management(sexProportions,"CALC_ATOTPOPBT","!ATOTPOPMT!+!ATOTPOPFT!","PYTHON")
            # create table view to avoid division by 0
            vTable = os.path.basename(sexProportions) + "_VIEW"
            vExpression = '"CALC_ATOTPOPBT" > 0'
            arcpy.MakeTableView_management(sexProportions, vTable, vExpression)  
            # add prop fields and calculate
            mProp = "ATOTPOPMTPROP"
            arcpy.AddField_management(vTable,mProp,"DOUBLE")
            mCalc = "float(!ATOTPOPMT!)/float(!CALC_ATOTPOPBT!)"
            arcpy.CalculateField_management(vTable,mProp,mCalc,"PYTHON")
            fProp = "ATOTPOPFTPROP"
            arcpy.AddField_management(vTable,fProp,"DOUBLE")
            fCalc = "float(!ATOTPOPFT!)/float(!CALC_ATOTPOPBT!)"
            arcpy.CalculateField_management(vTable,fProp,fCalc,"PYTHON")
            # create table view to fill in nulls
            # define view
            view0 = os.path.basename(sexProportions) + "_NULL"
            # define calculation expression
            expression0 = '"CALC_ATOTPOPBT" = 0' 
            arcpy.MakeTableView_management(sexProportions, view0, expression0)
            arcpy.CalculateField_management(view0, mProp, "0", "PYTHON")
            arcpy.CalculateField_management(view0, fProp, "0", "PYTHON")
            return "Calculated sex proportions for " + gdb
        
 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'F:\usa\tiles'
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
##        calcSexProportions(gdbItem)
    pool = multiprocessing.Pool(processes=35,maxtasksperchild=1)
    try:
        print pool.map(calcSexProportions, gdb_list)
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
