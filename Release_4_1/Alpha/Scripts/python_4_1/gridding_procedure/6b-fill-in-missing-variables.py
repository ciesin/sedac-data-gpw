# multiprocess template
import os, datetime
import multiprocessing
import arcpy
arcpy.CheckOutExtension('SPATIAL')
scriptTime = datetime.datetime.now()
def process(workspace):
    processTime = datetime.datetime.now()
    # parse input rasters
    # create the following variables E_A000_014MT,E_A000_014FT,E_A000_014BT,
    # E_A015_064MT,E_A015_064FT,E_A015_064BT,E_A015_049MT,E_A015_049BT
    try:
        variables = ["E_A000_014MT","E_A000_014FT","E_A000_014BT","E_A015_064MT",
                     "E_A015_064FT","E_A015_064BT","E_A015_049MT","E_A015_049BT"]
        for variable in variables:
            outRaster = workspace + os.sep + os.path.basename(workspace).upper() + "_" + variable + "_2010_CNTM.tif"
            startAge = variable[3:6]
            stopAge = variable[7:10]
            sex = variable[-2:]
            counterAge = int(startAge)
            expressionVariables = {}
            while counterAge<int(stopAge):
                counterAgeStop = counterAge + 4
                if len(str(counterAge))==1:
                    counterStart = "00" + str(counterAge)
                elif len(str(counterAge))==2:
                    counterStart = "0" + str(counterAge)
                else:
                    counterStart = str(counterAge)
                if len(str(counterAgeStop))==1:
                    counterStop = "00" + str(counterAgeStop)
                elif len(str(counterAgeStop))==2:
                    counterStop = "0" + str(counterAgeStop)
                else:
                    counterStop = str(counterAgeStop)
                expressionRaster = workspace + os.sep + os.path.basename(workspace).upper() + "_E_A" +counterStart+"_"+counterStop+sex+ "_2010_CNTM.tif"
                key = os.path.basename(workspace).upper() + "_E_A" +counterStart+"_"+counterStop+sex
                expressionVariables[key]=arcpy.Raster(expressionRaster)
                counterAge = counterAge + 5
            expressionString = ""
            for expressionKey in expressionVariables.keys():
                if expressionString == "":
                    expressionString = "expressionVariables["+'"'+expressionKey+'"'+"]"
                else:
                    expressionString = expressionString + " + expressionVariables["+'"'+expressionKey+'"'+"]"
            calcRaster = eval(expressionString)
            if arcpy.Exists(outRaster):
                arcpy.Delete_management(outRaster)
            arcpy.env.compression = "LZW"
            arcpy.CopyRaster_management(calcRaster,outRaster)
            arcpy.Delete_management(calcRaster)
        return ("Processed "+ workspace + " " + str(datetime.datetime.now()-processTime))
    except:
        return ("Error while processing " + workspace + " " + str(datetime.datetime.now()-processTime) + arcpy.GetMessages())
    
 

def main():
    workspace = r'D:\gpw\release_4_1\country_tifs'
    arcpy.env.workspace = workspace
    # must create procList
    procList = []
    countryList = arcpy.ListWorkspaces("*","FOLDER")
    for country in countryList:
        arcpy.env.workspace = country
        subFolders = arcpy.ListWorkspaces("*","FOLDER")
        if len(subFolders)==0:
            procList.append(country)
        else:
            for subFolder in subFolders:
                procList.append(subFolder)
    for ws in procList:
        print process(ws)
##    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
##    results = pool.map(process, procList)
##    for result in results:
##        print result
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
