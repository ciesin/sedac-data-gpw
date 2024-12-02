# Erin Doxsey-Whitfield
#
# Script checks whether any entire features in a country's boundaries
# are completely contained within the watermask.
# If yes, the validation fails.
#
# 3-20-15

# import libraries
import arcpy, os, datetime, csv

# define function to check if any boundary features are completely within watermask
def checkWaterMask(inBoundary, waterMask):
    # Make feature layer of inBoundary feature class
    inBoundaryLyr = inBoundary + os.sep + ".lyr"
    arcpy.MakeFeatureLayer_management(inBoundary,inBoundaryLyr)
    # Select all boundary features that are completely within the water mask
    arcpy.SelectLayerByLocation_management(inBoundaryLyr, "COMPLETELY_WITHIN", waterMask, "", "NEW_SELECTION")
    # Check if any features were selected
    result = arcpy.GetCount_management(inBoundaryLyr)
    count = int(result.getOutput(0))
    
    # If features selected, create list of selected UBIDs
    if count > 0:
        try:
            UBIDList = []
            rows = arcpy.da.SearchCursor(inBoundaryLyr,"UBID")
            for row in rows:
                UBIDList.append(str(row[0]))
            del rows
            validationDescription = "{} boundary features entirely within watermask. Boundaries must be addressed".format(count)
            validationResult = (0, count,UBIDList,validationDescription)
            return validationResult
        except Exception, e:
            print "\tList of selected UBIDs failed"
            print e
    # If no features selected, just return result
    else:
        UBIDList = []
        validationDescription = "No boundary features entirely within watermask. Boundaries are OK"
        validationResult = (1,count,UBIDList,validationDescription)
        return validationResult

# def main 
def main():
# set counter
    startTime = datetime.datetime.now()
    # define diagnosticTable
    diagnosticTable = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\validation\watermask_3_20_15.csv'
    # open csv file and write header
    csvFile = csv.writer(open(diagnosticTable,'wb'))
    csvFile.writerow(("country","valid","#Selected_UBIDs","UBID_List","Description"))
    # define working directory
####workspace will need to be changed for validation script
    workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
    arcpy.env.workspace = workspace

####Selecting the boundary and water mask is set up to test all the alpha boundaries.
####This will need to be amended for validation script
    # List File GDBs in workspace
    gdbList = arcpy.ListWorkspaces("*","FileGDB")
    gdbList.sort()
    # Iterate through gdbs
    for gdb in gdbList:
        processTime = datetime.datetime.now()
        arcpy.env.workspace = gdb
        # Parse ISO
        iso = os.path.basename(gdb)[:-4]
        print iso

        # Set default variables
        valid = 0
        selectCount = "N/A"
        UBIDList = []
        validationDescription = ""
        
        # List waterMask from each GDB
        waterMaskList = arcpy.ListFeatureClasses("*water_mask")
        if len(waterMaskList) > 1:
            validationDescription = "\tMore than 1 water mask fc.  There should only be 1."
            print validationDescription
        # If waterMask doesn't exist, then no issues with boundary.  Do not need to execute checkWaterMask function
        elif len(waterMaskList) == 0:
            valid = 1
            selectCount = 0
            validationDescription = "No watermask. Boundaries are OK"
            print validationDescription
        # If waterMask exists, then need to execute checkWaterMask function
        elif len(waterMaskList) == 1:
            for fc in waterMaskList:               
                waterMask = fc
                print "Water mask is " + waterMask
       
            # List inBoundary from each GDB. Exit if 0 or more than 1 boundary feature class exists.  Execute execute checkWaterMask function if list = 1
            boundaryList = arcpy.ListFeatureClasses("*boundaries_2010")
            if len(boundaryList) == 0:
                validationDescription = "\tMissing boundary fc"
                print validationDescription
            elif len(boundaryList) > 1:
                validationDescription = "\tMore than 1 boundary fc.  There should only be 1."
                print  validationDescription
            if len(boundaryList) == 1:
                for fc in boundaryList:
                    inBoundary = fc
                    print "Boundary is " + inBoundary
                # execute function
                    valid,selectCount,UBIDList,validationDescription = checkWaterMask(inBoundary, waterMask)
                    print valid,selectCount,UBIDList,validationDescription
        csvFile.writerow((iso,valid,selectCount,UBIDList,validationDescription))


#Summary of the output info
#    valid,              selectCount,               UBIDList,                   description
#    1(OK)/0(Not OK),    number of units selected, list of UBIDs selected,     text description 

        print "Completed " + iso
        print datetime.datetime.now() - processTime,"\n"

    print "Completed Script" 
    print datetime.datetime.now() - startTime

if __name__ == '__main__':
    main()
