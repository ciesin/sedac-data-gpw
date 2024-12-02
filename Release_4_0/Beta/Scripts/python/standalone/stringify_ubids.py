# multiprocess_template   

import os
import re
import multiprocessing
import arcpy
import imp, sys
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
 
def stringify(gdb):
    '''Worker function'''
    arcpy.env.workspace = gdb
    popFile = arcpy.ListTables("*pop_input")[0]
    if custom.checkFieldType(popFile,"UBID","String"):
        pass
    else:
        validationField = "UBID"
        tmpField = "STRING1"
        tmpCalc = 'int(!UBID!)'
        validationCalc = '!'+tmpField+'!' 
        try:
            arcpy.AddField_management(popFile,tmpField,"TEXT","","",255)
            arcpy.CalculateField_management(popFile,tmpField,tmpCalc,"PYTHON")
        except:
            sys.exit("The calculation failed")
        try:
            arcpy.DeleteField_management(popFile,validationField)
            arcpy.AddField_management(popFile,validationField,"TEXT","","",255)
            arcpy.CalculateField_management(popFile,validationField,validationCalc,"PYTHON")
            arcpy.DeleteField_management(popFile,tmpField)
        except:
            arcpy.GetMessages()
        print "Corrected " + popFile
 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of shapefiles
    workspace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
    arcpy.env.workspace = workspace
    gdbs = arcpy.ListWorkspaces('*')
    gdbs.sort()
    gdb_list = [os.path.join(workspace, gdb) for gdb in gdbs]
##    for gdb in gdbs:
##        stringify(gdb)
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
    pool.map(stringify, gdb_list)
 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    # End main
 
if __name__ == '__main__':
    main()
