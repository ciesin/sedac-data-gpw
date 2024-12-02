# multiprocess_template   

import os
import re
import multiprocessing
import arcpy
import imp, sys, datetime
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
 
def joinSexData(gdb):
    '''Worker function'''
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        pass
    else:
        popFile = arcpy.ListTables("*pop_input")[0]
        sexFile = arcpy.ListTables("*variables_input")[0]
        ##POPTABLEROWS = str(arcpy.GetCount_management(popFile)[0])
        ## maybe add similar validation from validate agr script here
        sexProportions = arcpy.ListTables("*sex_variables_proportions")[0]
        estimatesTable = str(popFile).replace("_input","_estimates")
        # check if estimatesFile contains valid data
        fData = "E_ATOTPOPFT_2010"
        mData = "E_ATOTPOPMT_2010"
##        if len(arcpy.ListFields(sexFile,"VARID"))<>1:
##            arcpy.AddField_management(sexFile,"VARID_SOURCE","TEXT","","",255)
##            arcpy.CalculateField_management(sexFile,"VARID_SOURCE",'"' + "UCADMIN0_UCADMIN1_UCADMIN2_UCADMIN3_UCADMIN4_UCADMIN5" + '"',"PYTHON")
##            arcpy.AddField_management(sexProportions,"VARID_SOURCE","TEXT","","",255)
##            arcpy.CalculateField_management(sexProportions,"VARID_SOURCE",'"' + "UCADMIN0_UCADMIN1_UCADMIN2_UCADMIN3_UCADMIN4_UCADMIN5" + '"',"PYTHON")
##            # expression
##        exp = "!UCADMIN0! + "+'"_"'+"!UCADMIN1! + "+'"_"'+"!UCADMIN2! + "+'"_"'+"!UCADMIN3! + "+'"_"'+"!UCADMIN4! + "+'"_"'+"!UCADMIN5!"
##            arcpy.AddField_management(sexFile,"VARID","TEXT","","",255)
##        arcpy.CalculateField_management(sexFile,"VARID",exp,"PYTHON")
##            arcpy.AddField_management(sexProportions,"VARID","TEXT","","",255)
##        arcpy.CalculateField_management(sexProportions,"VARID",exp,"PYTHON")


            
        dataFields = [fData,mData]
        for sData in dataFields:
            if len(arcpy.ListFields(estimatesTable,sData))<>1:
                print sData + " is missing"
                if sData == fData:
                    try:
                        arcpy.DeleteField_management(estimatesTable,["SPOPYEAR","SPOPLEVEL","VARID"])
                    except:
                        arcpy.GetMessages()
            else:
                # create views
                view = os.path.basename(gdb)[:-4]+sData + "_view"
                viewCalc = '"' + sData + '" IS NULL'
                if int(arcpy.GetCount_management(arcpy.MakeTableView_management(estimatesTable,view,viewCalc))[0])>0:
                    print sData + " has nulls"
            

 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of shapefiles
    workspace = r'E:\gpw\v4processing\inputs'
    usaSpace = r'E:\gpw\v4processing\inputs\usa\tiles'
    workspaces = [usaSpace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort(reverse=True)
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt) 
    for gdbItem in gdb_list:
        print gdbItem
        joinSexData(gdbItem)
##    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
##    pool.map(joinSexData, gdb_list)
## 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    # End main
 
if __name__ == '__main__':
    main()
