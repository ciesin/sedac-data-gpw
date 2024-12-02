# Kytt MacManus
# 10/27/16
# create a copy of the boundaries exported from sde which
# contains only ISO, GUBID, and UBID
# this script is executed on DEVSEDARC4

# import libraries
import arcpy, os, sys, multiprocessing
import datetime

def createGriddingBoundary(inFC):
    startTime = datetime.datetime.now()
    try:
        arcpy.env.overwriteOutput = True
        rootName = os.path.basename(inFC)
        iso = rootName[:3]
        outFolder = r'D:\gpw\release_4_1\input_data\gridding_boundaries'
        outGDB = outFolder + os.sep + iso.lower() + ".gdb"
        if not arcpy.Exists(outGDB):
            arcpy.CreateFileGDB_management(outFolder,iso.lower())    
        # copy the template boundaries to outGDB
        templateBoundaries = r'D:\gpw\release_4_1\loading\templates.gdb\gridding_boundaries'
        outFile = outGDB + os.sep + rootName + "_gridding"
        arcpy.CreateFeatureclass_management(outGDB,rootName + "_gridding","POLYGON",
                                            templateBoundaries,"DISABLED","DISABLED",
                                            arcpy.SpatialReference(4326))
        # append inFCG to outFile
        arcpy.Append_management(inFC,outFile,"NO_TEST")
        # calculate the ISO field
        arcpy.CalculateField_management(outFile,"ISO",'"' + iso.upper() + '"',"PYTHON")
        # success
        return rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return rootName + " error: " + str(arcpy.GetMessages()) 

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    fcs = arcpy.ListFeatureClasses("*")
    fcList = [os.path.join(inWS,fc) for fc in fcs]
##    for fc in fcList:
##        print fc
##        print createGriddingBoundary(fc)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    print pool.map(createGriddingBoundary, fcList) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
