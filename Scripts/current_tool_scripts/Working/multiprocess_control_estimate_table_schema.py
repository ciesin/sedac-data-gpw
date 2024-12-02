# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv, datetime, multiprocessing

def deleteFields(table):
    delFields = []
    # define estimate tables schema
    schemaFields = ["OBJECTID","OBJECTID_1","ID","USCID","UCADMIN0","NAME0","UCADMIN1","NAME1",
                    "UCADMIN2","NAME2","UCADMIN3","NAME3","UCADMIN4","NAME4","UCADMIN5","NAME5",
                    "UCADMIN6","NAME6","CENSUSYEAR","CENSUS_YEAR","ESTIMATE_YEAR","ATOTPOPBT",
                    "UCID0","UCID1","UCID2","UCID3","UCID4","UCID5","UCID6","UBID",
                    "ATOTPOPFT_PROP","ATOTPOPMT_PROP","ATOTPOPFU_PROP","ATOTPOPMU_PROP",
                    "ATOTPOPBU_PROP","ATOTPOPFR_PROP","ATOTPOPMR_PROP","ATOTPOPBR_PROP",
                    "YEARTO2000","YEARTO2005","YEARTO2010","YEARTO2015","YEARTO2020","AGR",
                    "E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPFT_2010",
                    "E_ATOTPOPMT_2010","E_ATOTPOPFU_2010","E_ATOTPOPMU_2010","E_ATOTPOPBU_2010",
                    "E_ATOTPOPFR_2010","E_ATOTPOPMR_2010","E_ATOTPOPBR_2010","E_ATOTPOPBT_2015",
                    "E_ATOTPOPBT_2020","UNADJFAC_2000","UNADJFAC_2005","UNADJFAC_2010","UNADJFAC_2015",
                    "UNADJFAC_2020","UNE_ATOTPOPBT_2000","UNE_ATOTPOPBT_2005","UNE_ATOTPOPBT_2010",                   
                    "UNE_ATOTPOPBT_2015","UNE_ATOTPOPBT_2020"]

    fields = arcpy.ListFields(table,"*")
    for field in fields:
        fldName = field.name
        if fldName in schemaFields:
            pass
        else:
            delFields.append(fldName)

    if len(delFields)>0:
        arcpy.DeleteField_management(table,delFields)
    
def main():
    startTime = datetime.datetime.now() 
    # Define Workspace Variable
    workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\estimates_tables_clean.gdb'

    # Assign workspace environment for ArcPy
    arcpy.env.workspace = workspace

    # List GDBs in workspace environment
    tables = arcpy.ListTables("*")
    tables.sort()
    for table in tables:
        delTime = datetime.datetime.now()
        deleteFields(table)
        print "Deleted fields in " + table
        print datetime.datetime.now() - delTime

##    pool = multiprocessing.Pool(processes=40)
##    pool.map(deleteFields, tables) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()

    print "Deleted Fields"
    print datetime.datetime.now() - startTime

if __name__ == '__main__':
    main()
