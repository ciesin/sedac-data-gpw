# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(fc):
    processTime = datetime.datetime.now()
    arcpy.CheckOutExtension("SPATIAL")
##    rootName = os.path.basename(fc).replace("_water_mask.shp","")
    rootName = os.path.basename(fc).replace("_admin0.shp","")
##    boundaryWS = r'D:\gpw\release_4_1\process' + os.sep + rootName + ".gdb"
##    if not arcpy.Exists(boundaryWS):
##        return "MISSING: " + boundaryWS
    boundaryWS = r'D:\gpw\release_4_1\loading\admin0_shps_v40'
    arcpy.env.workspace = boundaryWS
##    bfc = arcpy.ListFeatureClasses("*gridding")
    bfc = arcpy.ListFeatureClasses(rootName+"*")
    if len(bfc)==0:
        return fc + " is missing boundaries"
    else:
        bfc=bfc[0]
    clip = 'in_memory' + os.sep + rootName + 'clip'
    arcpy.Clip_analysis(fc,bfc,clip)
    symDiff = 'in_memory' + os.sep + rootName
    arcpy.SymDiff_analysis(fc,clip,symDiff)
##    wLyr = rootName + 'water'
##    bLyr = rootName + 'boundary'
##    arcpy.MakeFeatureLayer_management(fc,wLyr)
##    arcpy.MakeFeatureLayer_management(bfc,bLyr)
##    arcpy.SelectLayerByLocation_management(wLyr,"INTERSECT",bLyr,"#","NEW_SELECTION")
    if int(arcpy.GetCount_management(symDiff)[0])>0:
##        outFile = r'D:\gpw\release_4_1\water\water_problems'+os.sep + rootName + '.shp'
        outFile = r'D:\gpw\release_4_1\loading\admin_diff'+os.sep + rootName + '.shp'
        arcpy.CopyFeatures_management(symDiff,outFile)
        return "Created " + outFile
    else:
        return "No problem in " + rootName
    

def main():
##    workspace = r'D:\gpw\release_4_1\water\water_outputs\water_masks'
    workspace = r'D:\gpw\release_4_1\loading\admin0_shps'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    procList = [os.path.join(workspace,fc) for fc in arcpy.ListFeatureClasses("*")]
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
