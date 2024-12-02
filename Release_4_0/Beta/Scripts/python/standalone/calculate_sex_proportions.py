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
        if arcpy.Exists(sexProportions):
            pass
            #print sexProportions + " already exists"
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
            print "Calculated sex proportions for " + gdb
        
 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of shapefiles
    workspace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
    usaSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'
    braSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\bra\tiles'
    canSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\can\tiles'
    grlSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\grl\tiles'
    rusSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\rus\tiles'
    workspaces = [workspace]#,usaSpace,braSpace,canSpace,grlSpace,rusSpace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('ecu*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt) 
    
##    print len(gdb_list)
##
##    for i in gdb_list:
##        print i 
##
    for gdbItem in gdb_list:
        #print gdbItem
        calcSexProportions(gdbItem)
##    pool = multiprocessing.Pool(processes=35,maxtasksperchild=1)
##    #try:
##    pool.map(calcSexProportions, gdb_list)
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
##    except:
##        print sys.stdout
##        pool.close()
##        pool.join()
        
    # End main
    
 
if __name__ == '__main__':
    main()
