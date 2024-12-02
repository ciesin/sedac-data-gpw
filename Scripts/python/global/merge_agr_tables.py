# Kytt MacManus
# 3-19-15

# import libraries
import arcpy, os, datetime, csv, sys

# define function to check if a field exists in a feature class
def checkForField(inTable,field):
    flds = arcpy.ListFields(inTable,field)
    if len(flds)==1:
        return 1
    else:
        return 0


# define function to transfer table attributes as string into schema
def transferData(inTable, schemaTable):
    try:
        yearFail = 0
        # grab iso code
        iso = inTable[:3]
        # define agrTable
        agrTable = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr_csvs' + os.sep + iso +'.csv'
        if not arcpy.Exists(agrTable):
            # first determine which field will be used for an id field
            # check for USCID, then UBID, then AGRID
    ##        if checkForField(inTable,"USCID")==1:
    ##            AGRIDSOURCE = "USCID"
            if checkForField(inTable,"UBID")==1:
                AGRIDSOURCE = "UBID"
            elif checkForField(inTable,"USCID")==1:
                AGRIDSOURCE = "USCID"
            elif checkForField(inTable,"AGRID")==1:
                AGRIDSOURCE = "AGRID"
            else:
                print "There is no valid id field in " + inTable
            # next determine which field will be used for popyear
            # check for USCID, then UBID, then AGRID
            if checkForField(inTable,"CENSUS_YEAR")==1:
                POPYEAR = "CENSUS_YEAR"
                # create list of fields to return for search cursor
                cursorFields = [AGRIDSOURCE,POPYEAR]
            elif checkForField(inTable,"CENSUSYEAR")==1:
                POPYEAR = "CENSUSYEAR"
                # create list of fields to return for search cursor
                cursorFields = [AGRIDSOURCE,POPYEAR]
            elif checkForField(inTable,"ESTIMATE_YEAR")==1:
                POPYEAR = "ESTIMATE_YEAR"
                # create list of fields to return for search cursor
                cursorFields = [AGRIDSOURCE,POPYEAR]
            else:
                yearFail = 1
                # create list of fields to return for search cursor
                cursorFields = [AGRIDSOURCE]
            # create and iterate through list of schemaFields
            schemaFields = arcpy.ListFields(schemaTable,"*")
            for schemaField in schemaFields:
                # the agrid fields are new, so skip them
                if schemaField.name == "AGRID":
                    pass
                elif schemaField.name == "AGRID_SOURCE":
                    pass
                elif schemaField.name == "OBJECTID":
                    pass
                # otherwise check if the field exists
                else:
                    if checkForField(inTable,schemaField.name):
                        # if it exists then add it to the cursorFields list
                        cursorFields.append(schemaField.name)
            if yearFail == 1:
                header = ["ISO","AGRID_SOURCE","AGRID"] + cursorFields[1:]
            else:
                # define header and write to CSV
                header = ["ISO","AGRID_SOURCE","AGRID","POPYEAR"] + cursorFields[2:]
            print header
            # open csv file and write header
            csvFile = csv.writer(open(agrTable,'wb'))
            csvFile.writerow((header)) 
            # create search cursor and grab values to insert into csvFile
            valueList = [iso,AGRIDSOURCE]
            with arcpy.da.SearchCursor(inTable, cursorFields) as cursor:
                for cursorRow in cursor:
                    cursorValues = list(cursorRow)
                    rawValues = valueList + cursorValues
                    csvValues = [str(i) for i in rawValues]
                    print csvValues
                    # write to csv
                    csvFile.writerow((csvValues))
    except:
        os.remove(agrTable)
                       
   
        

# def main
def main():
    # set counter
    startTime = datetime.datetime.now()
    # define inSchema
    inSchema = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr.gdb\AGR_MERGED'
    # define working directory
    workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr_tables.gdb'
    arcpy.env.workspace = workspace
    # list tables
    tables = arcpy.ListTables("uzb*")
    tables.sort()
    for inTable in tables:
        processTime = datetime.datetime.now()
        print "Processing " + inTable[:3]
        country = inTable[:3]
        # execute function
        try:
            transferData(inTable,inSchema)
        except:
            if checkForField(inTable,"UBID")==0:
                estimatesTable = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\estimates_tables_clean.gdb' + os.sep + inTable[:3] + "_estimates"
                arcpy.JoinField_management(inTable,"USCID",estimatesTable,"USCID",["UBID"])
                transferData(inTable,inSchema)
            else:
                print "There is a problem with the UBID"
        print "Completed " + inTable
        print datetime.datetime.now() - processTime

    print "Completed Script"
    print datetime.datetime.now() - startTime

if __name__ == '__main__':
    main()
 
