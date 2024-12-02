# multiprocess_template   

import os
import re
import multiprocessing
import arcpy
import imp, sys
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
 
def calcSexProportions(gdb):
    '''Worker function'''
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        pass
    else:
        # define files to work with
        popFile = arcpy.ListTables("*pop_input")[0]
        sexFile = arcpy.ListTables("*sex_variables_input")[0]
        sexProportions = gdb + os.sep + sexFile.replace("_input","_proportions")
        estimatesFile = gdb + os.sep + popFile.replace("_input","_estimates")
        # check if the sexProportions is already existing
        if not arcpy.Exists(sexProportions):
            # first preprocess the sexFile
            # create output table
            arcpy.CopyRows_management(sexFile,sexProportions)
            # create table view to avoid division by 0
            
            vTable = os.path.basename(sexProportions) + "_VIEW"
            vExpression = '"ATOTPOPBT" > 0'
            arcpy.MakeTableView_management(sexProportions, vTable, vExpression)  
            
            # add prop fields and calculate
            mProp = "ATOTPOPMTPROP"
            arcpy.AddField_management(vTable,mProp,"DOUBLE")
            mCalc = "float(!ATOTPOPMT!)/float(!ATOTPOPBT!)"
            arcpy.CalculateField_management(vTable,mProp,mCalc,"PYTHON")
            fProp = "ATOTPOPFTPROP"
            arcpy.AddField_management(vTable,fProp,"DOUBLE")
            fCalc = "float(!ATOTPOPFT!)/float(!ATOTPOPBT!)"
            arcpy.CalculateField_management(vTable,fProp,fCalc,"PYTHON")
            # create table view to fill in nulls
            # define view
            view0 = os.path.basename(sexProportions) + "_NULL"
            # define calculation expression
            expression0 = '"ATOTPOPBT" = 0' 
            arcpy.MakeTableView_management(sexProportions, view0, expression0)
            arcpy.CalculateField_management(view0, mProp, "0", "PYTHON")
            arcpy.CalculateField_management(view0, fProp, "0", "PYTHON")
            print "Calculated sex proportions"
        else:
            print sexProportions + " already exists"
        
 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of shapefiles
    workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'
    arcpy.env.workspace = workspace
    gdbs = arcpy.ListWorkspaces('usa_nh*',"FILEGDB")
    gdbs.sort()
    gdb_list = [os.path.join(workspace, gdb) for gdb in gdbs]
    for gdb in gdbs:
        print gdb
        calcSexProportions(gdb)
##    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
##    pool.map(calcSexProportions, gdb_list)
## 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    # End main
 
if __name__ == '__main__':
    main()
