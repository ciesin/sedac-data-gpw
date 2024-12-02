
# import libraries
import arcpy, os, datetime, sys, multiprocessing
sys.path.insert(0, r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions')
from validateSchema import checkForField 

# load custom toolbox
arcpy.ImportToolbox(r'\\Dataserver0\gpw\GPW4\Beta\Scripts\toolboxes\ingest_and_validate_gpw4.tbx','landv')

def fixUS(iso):
    gdb = iso + ".gdb"
    iso = os.path.basename(iso)
    popSchemaTable = r'\\dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb\total_pop_admin5'
    sexSchemaTable = popSchemaTable.replace("total_pop","sex_variables")
    outGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\problem_states_step_1' + os.sep + iso + ".gdb"
    arcpy.env.workspace = gdb
    print gdb
    popTable = arcpy.ListTables("{}_admin*total_pop_raw".format(iso[:6]))[0]
    sexTable = arcpy.ListTables("{}_admin*sex_variables_raw".format(iso[:6]))[0]
    tables = [popTable,sexTable]
##    inputPopTable = popTable.replace("raw","input")
##    if arcpy.GetCount_management(inputPopTable)[0]==arcpy.GetCount_management(popTable)[0]:
##        print iso + " is already corrected"
##    else:
    # define schemaTable
    for table in tables:
        if table == popTable:
            schemaTable = popSchemaTable
        elif table == sexTable:
            schemaTable = sexSchemaTable
        else:
            print "table problemo"
            sys.exit()
        inputTable = table.replace("raw","input")
        # clean up input files
        try:
            if arcpy.Exists(inputTable):
                arcpy.Delete_management(inputTable)
                print "Deleted " + inputTable

            # recalculate name fields
            arcpy.CalculateField_management(table,"NAME2",'"COUNTY"',"PYTHON")
            arcpy.CalculateField_management(table,"NAME3",'"TRACT"',"PYTHON")
            arcpy.CalculateField_management(table,"NAME4",'"BLOCKGROUP"',"PYTHON")
            arcpy.CalculateField_management(table,"NAME5",'"BLOCK"',"PYTHON")
            print "Recalculated NAME fields"

            # copy schemaTable and append
            arcpy.CopyRows_management(schemaTable,inputTable)
            arcpy.Append_management(table,inputTable,"NO_TEST")
            print "Appended data for " + table
        except:
            print arcpy.GetMessages()


# def main
def main():
    # set workspace
    workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\problem_states_step_1'
    arcpy.env.workspace = workspace
    # define parameters list
    ingestParameters = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\ancillary.gdb\usa_fgdbs_8_19_15'

    # create search cursor to crawl ingest parameters
    isoList = ["usa_mt","usa_nc","usa_nd",
               "usa_ne","usa_nh","usa_nj",
               "usa_nm","usa_nv","usa_ny",
               "usa_oh","usa_ok","usa_og",
               "usa_pa","usa_sc"]
    iso_List = [os.path.join(workspace, iso) for iso in isoList]
    print iso_List
##    for iso in iso_List:
##        print iso
##        fixUS(iso)
    # create attribute pool for multiprocessing
    pool = multiprocessing.Pool(processes=12)
    pool.map(fixUS,iso_List)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
