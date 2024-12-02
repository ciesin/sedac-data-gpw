#Jane Mills
#3/29/2017
#Export everything to csv and shapefile
#correct iso codes we changed

# Import Libraries
import arcpy, os, re, multiprocessing, datetime
scriptTime = datetime.datetime.now()

def export(fcPath):
    returnList = []
    root = r'D:\gpw\release_4_1\centroids'
    template = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\ancillary.gdb\template'
    shpFolder = os.path.join(root,'shp')

    fc = os.path.basename(fcPath)
    iso = fc[:-10]
    
    if fc[:3] == 'usa':
        if fc[:5] == 'usaii':
            iso = 'usain'
        elif fc[:5] == 'usaog':
            iso = 'usaor'
    else:
        if fc[:3] == 'anr':
            iso = 'and'
        elif fc[:3] == 'vcs':
            iso = 'vat'

    #Save as shp
    outFC = os.path.join(shpFolder,iso+'_centroids.shp')
    arcpy.CopyFeatures_management(template,outFC)
    arcpy.Append_management(fcPath,outFC,"NO_TEST")

    returnList.append("Appended " + iso)
    return returnList


def main():
    centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\country_data.gdb'

    arcpy.env.workspace = centroids
    fcList1 = [os.path.join(centroids, f) for f in arcpy.ListFeatureClasses()]
    fcList2 = filter(lambda x: not 'usatx_centroids' == os.path.basename(x), fcList1)
    fcList2.sort()
    
    print "processing"

    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(export, fcList2)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)


if __name__ == '__main__':
    main()

