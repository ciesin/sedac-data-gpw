# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process3(gdb):
    outWS = r'D:\gpw\release_4_1\water\water_outputs\water_masks'
    arcpy.env.workspace = gdb
    waterFeatures = arcpy.ListFeatureClasses("*water_features")
    if len(waterFeatures)==0:
        return gdb + " has no water features"
    else:
        waterFeatures = waterFeatures[0]
    outFC = outWS + os.sep + waterFeatures.replace('features','mask')
    if not arcpy.Exists(outFC+".shp"):
        arcpy.CopyFeatures_management(waterFeatures,outFC)
        return "Created " + outFC
    else:
        return outFC + " already exists"
def process2(gdb):
    outWS = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
    arcpy.env.workspace = gdb
    estimates = arcpy.ListTables("*estimates")[0]
    adminLevel = estimates.split("_")[2]
    # grab inFC
    inFC = arcpy.ListFeatureClasses(os.path.basename(gdb)[:-4])
    if len(inFC)==0:
        inFC = arcpy.ListFeatureClasses("*gridding")[0]
    else:
        inFC = inFC[0]
    outFC = outWS + os.sep + inFC.split("_")[0]+"_"+inFC.split("_")[1]+"_"+adminLevel+"_boundaries_2010"
    if not arcpy.Exists(outFC):
        arcpy.CopyFeatures_management(inFC,outFC)
        return "Created " + outFC
    else:
        return outFC + " already exists"
    
def process(gdb):
    processTime = datetime.datetime.now()
    outWS = r'D:\gpw\release_4_1\input_data\pop_tables'
    outGDB = os.path.join(outWS,os.path.basename(gdb))
    if arcpy.Exists(outGDB):
        return outGDB + " already exists"
    else:
        try:
            arcpy.CreateFileGDB_management(outWS,os.path.basename(gdb)[:-4])
            arcpy.env.workspace = gdb
            estimates = arcpy.ListTables("*estimates")[0]
##            delFields = ["MASKEDADMINAREA"]
##            dsmFields = arcpy.ListFields(estimates,"*DSM")
##            for dsmField in dsmFields:
##                delFields.append(dsmField.name)
##            arcpy.DeleteField_management(estimates,delFields)
            arcpy.CopyRows_management(estimates,os.path.join(outGDB,os.path.basename(estimates)))
            return "processed " + estimates
        except:
            return arcpy.GetMessages()


def main():
    arcpy.env.workspace = r'D:\gpw\release_4_1\process_tiles'
    
    print "processing"
    # must create procList
    procList = arcpy.ListWorkspaces("can*")+arcpy.ListWorkspaces("grl*")
##    for gdb in procList:
##        print process2(gdb)
        
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(process3, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
