# create age and ur tables for the usa
# make copy of totalpop input, add appropriate fields and transfer attributes
# this script has custom considerations that may make it difficult to reuse in its entirety
# however there may be useful snippets for reuse
# Kytt MacManus

import arcpy, os, sys, datetime, multiprocessing

def populateTables(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:6]
    # define age fields
    ageFields = ['A000_004BT','A005_009BT','A010_014BT','A015_019BT','A020_024BT','A025_029BT',
                'A030_034BT','A035_039BT','A040_044BT','A045_049BT','A050_054BT','A055_059BT',
                'A060_064BT','A065_069BT','A070_074BT','A075_079BT','A080_084BT','A085plusBT']
    # define ur fields
    urFields = ['ATOTPOPBU','ATOTPOPBR','ATOTPOPFU','ATOTPOPFR','ATOTPOPMU','ATOTPOPMR']
    # also create combined list
    allFields = ['USCID'] + ageFields + urFields
    # set workspace
    arcpy.env.workspace = gdb
    # next grab the rawPop table
    try:
        popTable = arcpy.ListTables("*total_pop_input")[0]
        rawTable = arcpy.ListTables("*total_pop_raw")[0]
    except:
        return iso + ": is missing the total pop raw table"
    # create dictionary to hold values
    values = {}
    try:
        # read the values
        with arcpy.da.SearchCursor(rawTable,allFields) as cursor:
            for row in cursor:
                # store with USCID as key and a tuple of numbers as value
                key = row[0]
                value = row
                values[key] = value
    except:
        return "Error in " + iso + ": Creating Value Dictionary"
    try:
        # define new tables
        ageTable = popTable.replace("total_pop","age_5_year")
        urTable = popTable.replace("total_pop","ur")
        # write the age values
        with arcpy.da.UpdateCursor(ageTable,['USCID']+ageFields) as cursor:
            for row in cursor:
                # grab the USCID
                USCID = row[0]
                # set the age fields
                i = 1
                for ageField in ageFields:
                    row[i]=values[USCID][i]
                    i = i + 1
                # update the row
                cursor.updateRow(row)
        # write the ur values
        with arcpy.da.UpdateCursor(urTable,['USCID']+urFields) as cursor:
            for row in cursor:
                # grab the USCID
                USCID = row[0]
                # set the ur fields
                i = 1
                valueIndex = len(ageFields)+ 1
                for urField in urFields:
                    row[i]=values[USCID][valueIndex]
                    valueIndex = valueIndex + 1
                    i = i + 1
                # update the row
                cursor.updateRow(row)
    except:
        return "Error in " + iso + ": " + str(arcpy.GetMessages())

    # print total time to run
    return iso + ": " + str(datetime.datetime.now()-startTime)

def createTables(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:6]
    # define age fields
    ageFields = ['A000_004BT','A005_009BT','A010_014BT','A015_019BT','A020_024BT','A025_029BT',
                'A030_034BT','A035_039BT','A040_044BT','A045_049BT','A050_054BT','A055_059BT',
                'A060_064BT','A065_069BT','A070_074BT','A075_079BT','A080_084BT','A085plusBT']
    # define ur fields
    urFields = ['ATOTPOPBU','ATOTPOPBR','ATOTPOPFU','ATOTPOPFR','ATOTPOPMU','ATOTPOPMR']
    # set workspace
    arcpy.env.workspace = gdb
    # grab total pop table
    try:
        popTable = arcpy.ListTables("*total_pop_input")[0]
    except:
        return iso + ": is missing the total pop input table"
    # define new tables
    ageTable = popTable.replace("total_pop","age_5_year")
    urTable = popTable.replace("total_pop","ur")
    newTables = [ageTable,urTable]
    # make a copy of the total pop table for the age data and the ur data
    for newTable in newTables:
        arcpy.Copy_management(popTable,newTable)
        # add fields
        [arcpy.AddField_management(newTable,ageField,"DOUBLE")
         for ageField in ageFields if newTable == ageTable]
        [arcpy.AddField_management(newTable,urField,"DOUBLE")
         for urField in urFields if newTable == urTable]   
    # alter RPOPYEAR to variable appropriate name
    [arcpy.AlterField_management(newTable,"RPOPYEAR","APOPYEAR","APOPYEAR")
     for newTable in newTables if newTable == ageTable]
    [arcpy.AlterField_management(newTable,"RPOPYEAR","UPOPYEAR","UPOPYEAR")
     for newTable in newTables if newTable == urTable]
    # print total time to run
    return iso + ": " + str(datetime.datetime.now()-startTime)
    


def main():
    startTime = datetime.datetime.now()
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of files
    workspace = r'F:\gpw\pop_tables' # on machine devsedarc2
    workspaces = [workspace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt) 
##    for gdbItem in gdb_list:
##        print fixNames(gdbItem)
    print len(gdb_list)
    pool = multiprocessing.Pool(processes=28,maxtasksperchild=1)
    try:
        print pool.map(createTables, gdb_list)
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool.close()
        pool.join()
    except:
        print sys.stdout
        pool.close()
        pool.join()
    pool2 = multiprocessing.Pool(processes=28,maxtasksperchild=1)
    try:
        print pool2.map(populateTables, gdb_list)
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool2.close()
        pool2.join()
    except:
        print sys.stdout
        pool2.close()
        pool2.join()
        
    # End main
    print "Script Complete: " + str(datetime.datetime.now()-startTime)
    
 
if __name__ == '__main__':
    main()
