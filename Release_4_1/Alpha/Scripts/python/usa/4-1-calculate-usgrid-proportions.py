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
 
def calcUSgridProportions(gdb):
    '''Worker function'''
    arcpy.env.workspace = gdb
    # define files to work with
    pFile = arcpy.ListTables("*usgrids_pop_input")[0]
    pProportions = gdb + os.sep + pFile.replace("_input","_proportions")
##    hhFile = arcpy.ListTables("*usgrids_hh_input")[0]
##    hhProportions = gdb + os.sep + hhFile.replace("_input","_proportions")
    tbls = [pFile]#,hhFile]
    for tbl in tbls:
        if tbl == pFile:
            proportions = pProportions
            # create list of variables
            variables = ["!WHITE!","!BLACK!","!AMIND!","!ASIAN!","!HAWPI!",
                         "!HISP!","!NHISP!","!NHWHITE!","!NHBLACK!","!OTHER!",
                         "!TWOMORE!","!PUND25!","!P25!","!AUND1!","!A1TO4!",
                         "!A5TO17!","!A18TO24!","!A25TO64!","!A65TO79!","!AOV80!","!WOMCHILD!"]
        else:
            proportions = hhProportions
            # create list of variables
            variables = ["!HH!","!FEM!","!HU!","!OCC!","!OWN!","!SEA!","!HU1P!"]
        # check if the Proportions is already existing
        if arcpy.Exists(proportions):
            if len(arcpy.ListFields(proportions,"*WOMCHILD*"))<1:
                print "missing field"
                arcpy.Delete_management(proportions)
                # first preprocess the File
                # create output table
                arcpy.CopyRows_management(tbl,proportions)
##            else:
##                lyr=os.path.basename(proportions)+"v"
##                try:
##                    if int(arcpy.GetCount_management(
##                        arcpy.MakeTableView_management(
##                            proportions,lyr,"WOMCHILD_PROP IS NULL"))[0])>0:
##                        arcpy.Delete_management(lyr)
##                        return " No rows in: " + proportions
##                    arcpy.Delete_management(lyr)
##                except:
##                    return " FIX: " + proportions
            
        
        
                for variable in variables:
                    rawVariable = variable.replace("!","")
                    rawPropVariable = rawVariable + "_PROP"
                    # add prop fields and calculate
                    arcpy.AddField_management(proportions,rawPropVariable,"DOUBLE")
                    if tbl == pFile:
                        pCalc = "float(" + variable + ")/float(!POP!)"
                        expression0 = '"POP" = 0'
                    elif variable == "!HH!":
                        pCalc = "float(" + variable + ")/float(!HH!)"
                        expression0 = '"HH" = 0'
                    elif variable == "!FEM!":
                        pCalc = "float(" + variable + ")/float(!HH!)"
                        expression0 = '"HH" = 0'
                    else:
                        pCalc = "float(" + variable + ")/float(!HU!)"
                        expression0 = '"HU" = 0'
                    arcpy.CalculateField_management(proportions,rawPropVariable,pCalc,"PYTHON")
                    # create table view to fill in nulls
                    # define view
                    view0 = os.path.basename(proportions) + "_" + rawVariable + "_NULL"
                    # define calculation expression 
                    arcpy.MakeTableView_management(proportions, view0, expression0)
                    arcpy.CalculateField_management(view0, rawPropVariable, "0", "PYTHON")            
    return "Calculated usgrid proportions for " + gdb
        
 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'H:\gpw\stage\pop_tables'
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
    for gdbItem in gdb_list:
##        print gdbItem
        print calcUSgridProportions(gdbItem)
##    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
##    try:
##        print pool.map(calcUSgridProportions, gdb_list)
##        # Synchronize the main process with the job processes to
##        # ensure proper cleanup.
##        pool.close()
##        pool.join()
##    except:
##        print sys.stdout
##        pool.close()
##        pool.join()
        
    # End main
    
 
if __name__ == '__main__':
    main()
