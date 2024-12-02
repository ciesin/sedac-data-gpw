# population-estimates.py
# produce population estimates
# Kytt MacManus
# 2-11-13

# import libraries
import os, arcpy
import datetime
import multiprocessing

def pixelID(outWS):
    print "Processing"
    rootName = os.path.basename(outWS)[:-4]
    fishnet = outWS + os.sep + rootName + "_fishnet"
    fishnetClipped = outWS + os.sep + rootName + "_fishnet_clipped_intersect"
    fileList = [fishnet]#,fishnetClipped]
    for f in fileList:
        # first check that the UBID field exists in both the estimates and boundaries, if not exit
        if len(arcpy.ListFields(f,"PIXELID"))==1:
            print "The field already exists"
            pass         
        else:    
            fLyr = f + "_lyr"
            arcpy.MakeFeatureLayer_management(f,fLyr)
            arcpy.AddField_management(fLyr,"PIXELID","LONG")
            arcpy.CalculateField_management(fLyr,"PIXELID","!grid_code!","PYTHON")
            print "Calculated PixelID for " + f

def main():
    # set counter
    startTime = datetime.datetime.now()
    # define workspace
    workspace = r'E:\gpw\usa_state_v2\states'
    arcpy.env.workspace = workspace
    # list gdbs
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
##    pool = multiprocessing.Pool(processes=3)
##    pool.map(pixelID, gdbs) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()

    for gdb in gdbs:
        print gdb
        # define output workspace
        outWS = gdb
        pixelID(outWS)            
            
    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()
