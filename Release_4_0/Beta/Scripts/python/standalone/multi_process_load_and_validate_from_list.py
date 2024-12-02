# import libraries
import arcpy, os, datetime, sys, multiprocessing
# load custom toolbox
arcpy.ImportToolbox(r'\\Dataserver0\gpw\GPW4\Beta\Scripts\toolboxes\ingest_and_validate_gpw4.tbx')

def ingest(row):
    # parse row
    iso = row[1]
    populationTable = row[2]
    populationSheet = row[3]
    populationLevel = int(row[4])
    populationYear = int(row[5])
    yearField = "CENSUS_YEAR"
    sexTable = row[8]
    sexSheet = row[9]
    if row[10]==None:
        sexLevel = None
    else:
        sexLevel = int(row[10])
    lookupTable = row[6]
    lookupSheet = row[7]
    overWrite = True
    # set scratchDir
    scratchDir = r"\\dataserver0\gpw\GPW4\Beta\Gridding\country\scratch_dirs" + os.sep + iso
    if not arcpy.Exists(scratchDir):
        os.mkdir(scratchDir)
    arcpy.env.scratchWorkspace = scratchDir  
    # execute fuction
    arcpy.LoadAndValidateTables_landv(iso,populationTable,populationSheet,populationLevel,populationYear,
                                      yearField,sexTable,sexSheet,sexLevel,lookupTable,lookupSheet,overWrite)


def main():
 
    # set workspace
    workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
    arcpy.env.workspace = workspace

    # define parameters list
    ingestParameters = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\ancillary.gdb\ingest_parameters_8_17_15_0'

    # create search cursor to crawl ingest parameters
    rowsList = []
    with arcpy.da.SearchCursor(ingestParameters,"*") as rows:
        for row in rows:
            rowList = []
            for rowItem in list(row):
                rowList.append(rowItem)
            rowsList.append(rowList)
    rowsList  = rowsList[0:2]
    print rowsList
    # multiprocess the data
    pool = multiprocessing.Pool(processes=2,maxtasksperchild=1)
    pool.map(ingest, rowsList) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    
if __name__ == '__main__':
    main()        

        
