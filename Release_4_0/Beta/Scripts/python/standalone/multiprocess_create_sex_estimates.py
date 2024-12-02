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
        ##POPTABLEROWS = str(arcpy.GetCount_management(popFile)[0])
        ## maybe add similar validation from validate agr script here
        sexProportions = arcpy.ListTables("*sex_variables_proportions")[0]
        estimatesFile = str(popFile).replace("_input","_estimates")
        # check if estimatesFile already contains VARID
        if len(arcpy.ListFields(estimatesFile,"VARID"))>0:
            print arcpy.ListFields(estimatesFile,"VARID")
            print "VARID already exists"
        else:
            # need to also add and calculate VARID, and SPOPYEAR and SPOPLEVEL
            arcpy.AddField_management(estimatesFile,"VARID","TEXT","","",200)
            arcpy.AddField_management(estimatesFile,"SPOPYEAR","SHORT")
            arcpy.AddField_management(estimatesFile,"SPOPLEVEL","SHORT")
            # parse VARID_SOURCE to create expression and grab year
            with arcpy.da.SearchCursor(sexProportions,["VARID_SOURCE","RPOPYEAR"]) as rows:
                for row in rows:
                    VARIDSOURCE = str(row[0])
                    SPOPYEAR = int(row[1])
                    break
            # calculate level and year
            arcpy.CalculateField_management(estimatesFile,"SPOPYEAR",SPOPYEAR,"PYTHON")
            print "Calculated SPOPYEAR = " + str(SPOPYEAR)
            SPOPLEVEL = len(VARIDSOURCE.split("_"))-1
            arcpy.CalculateField_management(estimatesFile,"SPOPLEVEL",SPOPLEVEL,"PYTHON")
            print "Calcultat SPOPLEVEL = " + str(SPOPLEVEL)
            # parse VARID   
            for varItem in VARIDSOURCE.split("_"):
                if varItem == VARIDSOURCE.split("_")[0]:
                    expression = "!" + varItem + "!"
                else:
                    expression = expression + '+"_"+' + "!" + varItem + "!"
            print "VARID_SOURCE = " + VARIDSOURCE
            print "Expression = " + expression
            arcpy.CalculateField_management(estimatesFile,"VARID",expression,"PYTHON")
            print "Calculated VARID"
            # define joinFields and join
            joinFields = ["ATOTPOPMTPROP","ATOTPOPFTPROP"]
            arcpy.JoinField_management(estimatesFile,"VARID",sexProportions,"VARID",joinFields)
            print "Joined Proportions Fields"
            # add and calculate E_ATOTPOPFT_2010 and E_TOTPOPMT_2010
            arcpy.AddField_management(estimatesFile,"E_ATOTPOPFT_2010","LONG")
            arcpy.AddField_management(estimatesFile,"E_ATOTPOPMT_2010","LONG")
            arcpy.CalculateField_management(estimatesFile,"E_ATOTPOPFT_2010",
                                            "!E_ATOTPOPBT_2010! * !ATOTPOPFTPROP!","PYTHON")
            arcpy.CalculateField_management(estimatesFile,"E_ATOTPOPMT_2010",
                                            "!E_ATOTPOPBT_2010! * !ATOTPOPMTPROP!","PYTHON")
            print "Calculated 2010 MT and FT"

 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of shapefiles
    workspace = r'E:\gpw\v4processing\inputs'
    usaSpace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'
    workspaces = [usaSpace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('usa_nh*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt) 
##    for gdbItem in gdb_list:
##        print gdbItem
##        joinSexData(gdb)
    pool = multiprocessing.Pool(processes=8,maxtasksperchild=1)
    pool.map(joinSexData, gdb_list)
 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    # End main
 
if __name__ == '__main__':
    main()
