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
    diagnosticTable = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Changes_for_Prod_management\watermask_2_2_16.csv'
    # open csv file and write header
    csvFile = csv.writer(open(diagnosticTable,'wb'))
    csvFile.writerow(("country","valid","#Selected_UBIDs","UBID_List","Description"))
    # define working directory
####workspace will need to be changed for validation script
    workspace = r'\\Dataserver0\gpw\GPW4\Release_4_0\Beta\Gridding\global\features\from_sde\country_boundaries_hi_res.gdb'
    arcpy.env.workspace = workspace

####Selecting the boundary and water mask is set up to test all the alpha boundaries.
####This will need to be amended for validation script
    boundaryList = arcpy.ListFeatureClasses()
    for fc in boundaryList:
        processTime = datetime.datetime.now()
        inBoundary = fc
        # Parse ISO
        iso = os.path.basename(fc)[:3]
        print iso

        # Set default variables
        valid = 0
        selectCount = "N/A"
        UBIDList = []
        validationDescription = ""

        # If waterMask exists, then need to execute checkWaterMask function
        waterMask = r'\\Dataserver0\gpw\GPW4\Release_4_0\Beta\Gridding\ancillary.gdb\water_mask_final'
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
