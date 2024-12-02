# John Squires
# 3-23-15

# import libraries
import arcpy, xlrd
# and from other scripts which should be moved to a gpw_validation module
import validate_schema

def get_excel_column_values(workbook, sheet, colHead):
    '''
    Returns a list of non-empty Excel values from the `colHead` column.

    Arguments:
        workbook : str
            location of Excel workbook to open
        sheet : str
            name of sheet to process
        colHead : str
            header to process, from first row of sheet
    Returns:
        colValues : list of str
    '''
    workbook = xlrd.open_workbook(workbook)
    worksheet = workbook.sheet_by_name(sheet)
    # get objects from the first row
    headers = worksheet.row(0)
    colValues = []
    colnum = 0
    for h in headers:
        if h.value == colHead:
            colObjects = worksheet.col(colnum)
            # skip first object which contains the header
            for co in colObjects[1:]:
                # only append non-empty cells
                if not co.ctype == 0:
                    colValues.append(co.value)
            return colValues
        colnum += 1

def list_duplicates(values, check="dupes"):
    """
    Checks list of ids for duplicates then returns list of duplicates.
    When check argument is "unique", returns unique values instead.
    """
    seen = set()
    add_to_seen = seen.add # used to save time
    # adds all unique elements to seen and all others to seen_twice
    seen_twice = set( x for x in values if x in seen or add_to_seen(x) ) 
    if check == "unique":
        return list(seen)
    else:
        return list(seen_twice)

arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Scripts\python\global'
inExcel = "TEST_SCRIPT.xlsx"
inSheet = r'TEST_SCRIPT.xlsx\abw_admin2_census_2010$'
inSheet2 = "abw_admin2_census_2010"
idsToCheck = ["UBID", "USCID", "NODUPES"]
duplicates = []

# xlrd method
def main4():
    for idToCheck in idsToCheck:
        if validate_schema.checkForField(inSheet,idToCheck):
            print "\nTesting {}s for duplicates:".format(idToCheck)
            idValues = get_excel_column_values(inExcel, inSheet2, idToCheck)
            print "idValues from xlrd: {}\n".format(idValues)
            duplicates = list_duplicates(idValues)
            if not duplicates:
                print "A: 0 {} duplicates found".format(idToCheck)
                print duplicates
                # write to csv
            else:
                print "B: {0} {1} duplicate(s) found:".format(len(duplicates),idToCheck)
                formattedDuplicates = ','.join(map(str, duplicates))
                print formattedDuplicates
                # write message and ids to csv
        else:
            #probably want to explicitely name the table
            print "C: {} not found in table".format(idToCheck)
           
if __name__ == '__main__':
   # main()
    #print "\nTake 2:"
    #main2()
    #print "\nTake 3:"
    #main3()
    main4()

#OLD METHODS
# cursor method on tableView
##def main():
##    #whereClause = "["+idToCheck+"]"
##    #print "whereClause: " + whereClause
##    arcpy.MakeTableView_management(inSheet, "tableView")
##    for idToCheck in idsToCheck:
##        if validate_schema.checkForField(inSheet,idToCheck):
##            print "Testing {}s for duplicates".format(idToCheck)
##            with arcpy.da.SearchCursor("tableView", idToCheck) as cursor:
##                #START testing adding rows to list
##                idValues = []
##                for row in cursor:
##                     idValues.append(row)
##                #END test    
##                duplicates = list_duplicates(idValues)
##                if not duplicates:
##                    print "A: 0 {} duplicates found".format(idToCheck)
##                    print duplicates
##                    # write to csv
##                else:
##                    print "B: {0} {1} duplicate(s) found".format(len(duplicates),idToCheck)
##                    formattedDuplicates = ','.join(map(str, duplicates))
##                    print formattedDuplicates
##                    # write message and ids to csv
##        else:
##            #probably want to explicitely name the table
##            print "C: {} not found in table".format(idToCheck)
##            
### cursor method on Excel file
##def main2():
##    for idToCheck in idsToCheck:
##        if validate_schema.checkForField(inSheet,idToCheck):
##            print "Testing {}s for duplicates".format(idToCheck)
##            with arcpy.da.SearchCursor(inSheet, idToCheck) as cursor:
##                duplicates = list_duplicates(cursor)
##                if not duplicates:
##                    print "A: 0 {} duplicates found".format(idToCheck)
##                    print duplicates
##                    # write to csv
##                else:
##                    print "B: {0} {1} duplicate(s) found".format(len(duplicates),idToCheck)
##                    formattedDuplicates = ','.join(map(str, duplicates))
##                    print formattedDuplicates
##                    # write message and ids to csv
##        else:
##            #probably want to explicitely name the table
##            print "C: {} not found in table".format(idToCheck)
##            
### create dbf method        
##def main3():
##    inTable = "test_table"
##    arcpy.ExcelToTable_conversion(inExcel, inTable)
##    for idToCheck in idsToCheck:
##        if validate_schema.checkForField(inSheet,idToCheck):
##            print "Testing {}s for duplicates".format(idToCheck)
##            with arcpy.da.SearchCursor(inTable,idToCheck) as cursor:
##                duplicates = list_duplicates(cursor)
##                if not duplicates:
##                    print "A: 0 {} duplicates found".format(idToCheck)
##                    print duplicates
##                    # write to csv
##                else:
##                    print "B: {0} {1} duplicate(s) found".format(len(duplicates),idToCheck)
##                    formattedDuplicates = ','.join(map(str, duplicates))
##                    print formattedDuplicates
##                    # write message and ids to csv
##        else:
##            #probably want to explicitely name the table
##            print "C: {} not found in table".format(idToCheck)
